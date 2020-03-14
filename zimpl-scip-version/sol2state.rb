#
# this script generates state-files from solution files. state files can be viewed in contour.
#
require 'rexml/document' #loads the REXML library
require 'pp'
require 'date' #For timestamp

include REXML #include the REXML namespace

def getBoundaryNodeFlowIn(solutionfile)
	flow_in = {}
	File.readlines(solutionfile).each do |line|
		data = line.match(/var_node_Qo_in\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			flow_in[data[1]] = data[2].to_f.round(3).to_s
		end
	end
	flow_in
end

def setBoundaryNodeFlowIn(stateXml,inflow)
	stateXml.elements.each("//boundaryNodes/*") do |e|
		al = e.attributes['alias']
		e.elements["inflow"].attributes["value"] = inflow[al]
	end
end

# get node pressures in barg
def getNodePressures(solutionfile)
	ps = {}
	File.readlines(solutionfile).each do |line|
		data = line.match(/var_node_p\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			ps[data[1]] = (data[2].to_f - Barg2Bar).round(3).to_s
		end
	end
	ps
end

def setNodePressures(stateXml, pressures)
	stateXml.elements.each("//nodes/*/*") do |e|
		al = e.attributes["alias"]
		e.elements["pressure"].attributes["value"] = pressures[al]
	end
end

def mean(a,b)
	return (a+b)/2.0
end

def getPipeFlow(solutionfile)
	flow = {}
	File.readlines(solutionfile).each do |line|
		data = line.match(/var_pipe_Qo_(out|in)\$([^\s]*)\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			key = data[2] + "^" + data[3]
			if flow.has_key? key
				flow[key] = mean(flow[key].to_f, data[4].to_f)
			else
				flow[key] = data[4].to_f.round(3).to_s
			end
		end
	end
	flow
end

def setPipeFlow(stateXml, flow)
	stateXml.elements.each("//connections/pipe") do |e|
		al= e.attributes['alias']
		e.elements["flow"].attributes["value"] = flow[al]
	end
end

def getNonPipeFlow(solutionfile)
	flow = {}
	File.readlines(solutionfile).each do |line|
		data = line.match(/var_non_pipe_Qo\$([^\s]*)\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			key = data[1] + "^" + data[2]
			flow[key] = data[3].to_f.round(3).to_s
		end
	end
	flow
end

def setNonPipeFlow(stateXml, flow)
	stateXml.elements.each("//connections/*") do |e|
		if e.name != "pipe"
			al = e.attributes['alias']
			e.elements["flow"].attributes["value"] = flow[al]
		end
	end
end

def getDragFactor(solutionFile)
	df = {}
	File.readlines(solutionFile).each do |line|
		data = line.match(/zeta_DA\$([^\s]*)\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			key = data[1] + "^" + data[2]
			df[key] = data[3].to_f.round(3).to_s
		end
	end
	df
end

def setDragFactor(stateXml, dragFactor)
	stateXml.elements.each("//connections/resistor") do |e|
		al = e.attributes['alias']
		e.elements["dragFactor"].attributes["value"] = dragFactor[al]
	end
end

def openClosed(val)
	if val == "1"
		"open"
	else
		"closed"
	end
end

def getValveMode(solutionFile)
	va = {}
	File.readlines(solutionFile).each do |line|
		data = line.match(/va_DA\$([^\s]*)\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			key = data[1] + "^" + data[2]
			va[key] = openClosed(data[3])
		end
	end
	va
end

def setValveMode(stateXml, modes)
	stateXml.elements.each("//connections/valve") do |e|
		al = e.attributes['alias']
		e.elements["mode"].attributes["value"] = modes[al]
	end
end

def closedFree(val)
	if val == "1" 
		"free"
	else
		"closed"
	end
end

def getCompressorConfig(solutionFile)
	cs = {}
	File.readlines(solutionFile).each do |line|
		data = line.match(/compressor_DA\$([^\s]*)\$([^\s]*)\s*([^\s]*)/)
		if !data.nil?
			key = data[1] + "^" + data[2]
			cs[key] = closedFree(data[3])
		end
	end
	cs
end

def setCompressorConfig(stateXml, configs)
	stateXml.elements.each("//connections/compressorStation") do |e|
		al = e.attributes['alias']
		e.attributes["configuration"] = configs[al]
	end
end

Barg2Bar = 1.01325

def sol2state(solFile,timestamp)
	old = (File.basename(solFile)).scan(/(\d+)/).join('') #file name for each iteration

	stateFile = File.open("../netstate/state_#{old}.xml", "w")
	stateTemplate = File.open("../netstate/state_sim.xml", "r")

	if (File.exist?(stateTemplate))
		stateFile.write(stateTemplate.read())
	end
	stateTemplate.close()

	doc = Document.new(File.open(stateFile))

	el = doc.elements['//timeOfState/']
	el.attributes['timestamp'] = timestamp #Time in YYYY-MM-DDThh:mm:ss 

	setBoundaryNodeFlowIn(doc, getBoundaryNodeFlowIn(solFile))
	setNodePressures(doc, getNodePressures(solFile))
	setPipeFlow(doc, getPipeFlow(solFile))
	setNonPipeFlow(doc, getNonPipeFlow(solFile))
	setDragFactor(doc, getDragFactor(solFile))
	setValveMode(doc, getValveMode(solFile))
	setCompressorConfig(doc, getCompressorConfig(solFile))

	File.write(stateFile, doc)
	formatter = Formatters::Pretty.new(5)
	formatter.compact = true
	formatter.write(doc, File.open(stateFile,"w"))
	stateFile.close()
end
