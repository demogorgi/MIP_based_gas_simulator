#
# this script generates start values for the simulator in zimpl format from create_netstate state-file
#

require 'rexml/document'

Barg2Bar = 1.01325

# get all node pressures from stateXml in bar
def getNodePressures(stateXml)
	ps = {}
	stateXml.elements.each("//nodes/*/*") do |e|
		ps[e.attributes["alias"]] = e.elements["pressure"].attributes["value"].to_f + Barg2Bar
	end
	ps
end

# get all connection flows from stateXml
def getConnectionsFlow(stateXml)
	pipe_qs = {}
	non_pipe_qs = {}
	no_flow = []
	stateXml.elements.each("//connections/*") do |e|
		if e.name == "pipe"
			pipe_qs[e.attributes["alias"]] = e.elements["flow"].attributes["value"].to_f
		else
			begin
				non_pipe_qs[e.attributes["alias"]] = e.elements["flow"].attributes["value"].to_f
			rescue
				no_flow << e.attributes["alias"]
				puts "Non pipe element <\"#{e.attributes["alias"].sub("^","\", \"")}\"> has no flow element."
			end
		end
	end
	[pipe_qs, non_pipe_qs, no_flow]
end

# replace last comma by semicolon according to zimpl language
def formatter(str)
	str.match(/(.*),/m)[1] + ";\n\n"
end

# scenario directory as argument
scenarioDir = ARGV[0]

# state-file
stateFile = File.open(scenarioDir + "/netstate/state_sim.xml","r")

# state-xml
stateXml = REXML::Document.new(File.open(stateFile))

# start values for node pressures
node_ps = getNodePressures(stateXml)

# start values for connection flows
pipe_qs, non_pipe_qs, no_flow = getConnectionsFlow(stateXml)

# start values for node pressures into var_node_p_old_0000.zpl
node_p_content = "# Pressure old in bar\nparam var_node_p_old[NO] :=\n"
node_ps.each{ |k,v| node_p_content += "<\"#{k}\"> #{v},\n" }

# start values for non pipe flows into var_non_pipe_Qo_old_0000.zpl
non_pipe_q_content = "# Flow old non-pipes in 1000 m³/h\nparam var_non_pipe_Qo_old[CN without P] :=\n"
non_pipe_qs.each{ |k,v| non_pipe_q_content +=  "<\"#{k.sub("^","\", \"")}\"> #{v},\n" }

# start values for pipe flows into var_pipe_Qo_in_old_0000.zpl and var_pipe_Qo_out_old_0000.zpl
pipe_q_content = "# Flow old for pipes in 1000 m³/h\nparam var_pipe_Qo_in_old[P] :=\n"
pipe_qs.each{ |k,v| pipe_q_content +=  "<\"#{k.sub("^","\", \"")}\"> #{v},\n" }

File.open(scenarioDir + "/vars_old_0000.zpl","w+") { |file| file.write( formatter(node_p_content) + formatter(non_pipe_q_content) + formatter(pipe_q_content) + formatter(pipe_q_content.gsub("_in_", "_out_")) ) }
File.open(scenarioDir + "/vars_old_old_0000.zpl","w+") { |file| file.write( (formatter(node_p_content) + formatter(non_pipe_q_content) + formatter(pipe_q_content) + formatter(pipe_q_content.gsub("_in_", "_out_"))).gsub("_old","_old_old") ) }

