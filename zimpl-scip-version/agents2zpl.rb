require 'yaml'

def generateDecisionsZpl(decisionsYmlFile,zplFile,decisions_old)
	if File.exist?(decisionsYmlFile)
		decisionsHash = YAML.load_file(decisionsYmlFile)
	else
		decisionsHash = {}
	end

	if decisions_old.empty?()
		decisions_old = decisionsHash
	end

	decisionsHash.each{ |k,v|
		v.each{ |sk,sv|
			if !sv.nil?
				sv.each{ |ssk,ssv| decisions_old[k][sk][ssk] = ssv }
			end
		}
	}

	decisions = decisions_old

	content = ""
	decisions.each{ |parameter, set|
		set.each{ |set_name, elements|
			content += "param #{parameter}[#{set_name}] := \n"
			tmp = ""
			if elements.nil?
				content += "<> 0;"
			else
				elements.each{ |name, value|
					tmp += "<\"#{name}\"\> #{value},\n"
				}
				content += tmp.gsub("^","\", \"").sub(/(.*),/m,'\1;') + "\n"
			end
		}
	}
	puts "\n>>>>>>>>>>>>>>>>>>> agents decisions >>>>>>>>>>>>>>>>>>>>>>\n\n"
	puts content
	puts "\n<<<<<<<<<<<<<<<<<<< agents decisions<<<<<<<<<<<<<<<<<<<<<<<\n\n"
	File.write(zplFile, content)
	return decisions
end
