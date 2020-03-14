# 
# this script handels the whole process
#
#require "profile"

# generate gnuplot compressor wheel maps
Gnuplot = false

require "./agents2zpl.rb"
require "./sol2state.rb"
require 'fileutils'

# generate static_data.zpl - this is manly topology information in zompl format
puts netstate2zpl = "ruby netstate2zpl.rb #{ARGV[2]}"
system(netstate2zpl)

# generate start value-files - the required start values vars_old_0000.zpl and vars_old_old_0000.zpl in zimpl format
puts state2start = "ruby state2start.rb #{ARGV[2]}"
system(state2start)

# number of simulation time steps
numTimesteps = ARGV[0].to_i 
# length of simulation time steps
lengthTimesteps = ARGV[1].to_f # in seconds
lengthTimesteps ||= 180
# first timestamp
timestamp = Time.now

# ARGV[2] is the direstory with scenario denpendent data such as simulator_static.zpl and net_sim.xml and state_sim.xml
Dir.chdir(ARGV[2])
sim_states = Dir.glob("./netstate/*.xml").select{ |f| f =~ /state_[0-9]+/ }
FileUtils.rm(sim_states)
Dir.mkdir("output") unless File.exists?("output")
Dir.chdir("output")
FileUtils.rm(Dir.glob("*.{scip,lp,tbl,zpl,sol,pdf,tmp}"))
FileUtils.cp(Dir.glob("../*0000*"),".")

old = nil
# dictonary that contains network control and boundary values
decisions = {}
# array of values that are used compute agent and dispatcher penalties
agent_penalties = []
# main loop
(0..numTimesteps).each do |t|
	# prerequisites
	timestamp += lengthTimesteps
	puts "\n#################"
	puts "# step #{t} / #{numTimesteps}"
	puts "#################\n\n"
	old = t.to_s.rjust(4,"0")
	if t == 0
		old_old = old
	else
		old_old = (t-1).to_s.rjust(4,"0")
	end
	new = (t+1).to_s.rjust(4,"0")
	
	###############################
	# LP erzeugen: Zimpl-Aufruf mit letztem Zustand. Parameter werden mit -D übergeben.
	# generate zpl from agents decisions yaml-file
	decisions = generateDecisionsZpl("agents_decisions_#{old}.yml", "agents_decisions_#{old}.zpl", decisions)
	
	# build zimpl command for next timestep
	puts zimpl_cmd = "zimpl -l 100 -D dt=#{lengthTimesteps} -D iteration=#{t} -o simulator_#{old}"\
	" ../simulator_static_data.zpl"\
		" agents_decisions_#{old}.zpl"\
		" vars_old_#{old}.zpl"\
		" vars_old_old_#{old_old}.zpl"\
		" ../../simulator_model.zpl"
	# execute zimpl
	zout = `#{zimpl_cmd}`

	puts "\n>>>>>>>>>>>>>>>>>>> zimpl output start >>>>>>>>>>>>>>>>>>>>>>\n\n"
	puts zout
	puts "\n<<<<<<<<<<<<<<<<<<< zimpl output end <<<<<<<<<<<<<<<<<<<<<<<<\n\n"

	if Gnuplot
		gnuplot_cmd = zout.match(/(?<=__GNUPLOT__;).*/)
		unless gnuplot_cmd.nil?
			puts "\n>>>>>>>>>>>>>>>>>>> gnuplot output start >>>>>>>>>>>>>>>>>>>>\n\n"
			puts "#{(gnuplot_cmd[0] + "").gsub!(";", "\n")}"
			puts "\n<<<<<<<<<<<<<<<<<<< gnuplot output end <<<<<<<<<<<<<<<<<<<<<<\n\n"
			system("gnuplot -e \"#{gnuplot_cmd}\"")
		end
	end

	puts "\n>>>>>>>>>>>>>>>>>>> optimizer output start >>>>>>>>>>>>>>>>>>\n\n"
	if ARGV[3] == "grb"
		out = `python3 ../../grb.py simulator_#{old}.lp`
		puts out
		# IIS-generation only available if gurobi is used
		if out.include?("Model is infeasible")
			puts "\n\n################################################################"
			puts "Model is infeasible. Compute irreducible inconsistent subsystem."
			puts "################################################################\n\n"
			system("python3 ../../grbIIS.py simulator_#{old}.lp")
		end
	else
		# Scip-Datei erzeugen.
		File.write("doIt.scip", "set write printzeros TRUE\nr simulator_#{old}.lp\no\nw solu simulator_#{old}.sol\nq\n")
		# Scip-Aufruf mit erzeugter LP-Datei und erzeugter .scip-Datei.
		system("scip < doIt.scip")
	end
	puts "\n<<<<<<<<<<<<<<<<<<< optimizer output end <<<<<<<<<<<<<<<<<<<<\n\n"

	###############################
	# Berechnete Drücke und Flüsse holen, diese werden zur Approximation von Druck- und Flussquadraten im Simulatormodell verwendet
	vars = `grep -E \"^var_[^b].*\\\\$\" simulator_#{old}.sol`.split("\n")
	# Berechnete Drücke und Flüsse in handliches Dictionary überführen
	vars_nice = vars.map{ |a| a.sub(/ \t.*$/,"").gsub(/\s+/,"§").sub("$","§").sub("$","^").split("§") }
	vars_nice.map{ |a|
		if a[0] =~ /node/
			a[0] = "param " + a[0] + "_old[NO] :=\n"
		elsif a[0] =~ /non/
			a[0] = "param " + a[0] + "_old[CN without P] :=\n"
		else
			a[0] = "param " + a[0] + "_old[P] :=\n"
		end
	}
	# noch handlicher, da schon fast zimpl
	vars_nicer = vars_nice.group_by{ |a| a[0] }
	vars_nicer.each{ |k,v|
		v.map!{ |a|
			if a[0] =~ /node/
                            "<\"#{a[1]}\"> #{a[2]}"
			else
                            "<\"#{a[1].sub("^","\", \"")}\"> #{a[2]}"
			end
		}
	}
	# Dictionary in Zimpl-Datei überführen
	vars_zpl = ""
	vars_nicer.each{ |k,v|
		vars_zpl += k
 		vars_zpl += v.join(",\n")
		vars_zpl += ";\n\n"
	}
	File.open("vars_old_#{new}.zpl", 'w') {|f| f.write vars_zpl } 
	File.open("vars_old_old_#{new}.zpl", 'w') {|f| f.write vars_zpl.gsub("_old","_old_old") } 

	###############################
	# create state-file from solution-file
	sol2state("simulator_#{old}.sol", timestamp.strftime("%Y-%m-%dT%H:%M:%S"))

	###############################
	# For agent penalty computation
	agent_penalties << `grep -E \"_[DT]A\" simulator_#{old}.sol`.split("\n")
	agent_penalties.flatten!()

	# Store penalty information in array
	ap_nice = agent_penalties.map{ |a| a.sub(/ \t.*$/,"").gsub(/\s+/,"§").sub("$","§").sub("$","^").split("§") }

	# Store penalty information in dictionary
	penalties = {}
	ap_nice.map{ |x| x[0] }.uniq
	ap_nice.each{ |a|
		if a.length == 3
			penalties[a[0]] ||= {}
			penalties[a[0]][a[1]] ||= []
			if a[0] =~ /pressure/
				y = [0.0, a[2].to_f].max
			elsif a[0] =~ /(compressor_DA|va_DA)/
				y = a[2].to_i # discrete decisions
			else
				y = a[2].to_f
			end
			penalties[a[0]][a[1]] << y
		elsif a.length == 2
			penalties[a[0]] ||= []
			penalties[a[0]] << a[1].to_f
		else
			raise IndexError, 'Array length not 2 or 3 should never happen here'  
		end
	}

	# Store penalty information in yaml-file
	File.open('agent_penalties.yml', 'w') {|f| f.write penalties.to_yaml } 
end

# delete old compressor wheel map plots
if File.exist?("all.pdf")
	File.delete("all.pdf")
end

# generate new compressor wheel map plot
if Gnuplot
	system("pdftk *.pdf cat output all.pdf")
end

