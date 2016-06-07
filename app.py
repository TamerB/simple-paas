import os
import jenkins
import re
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showJavaBuild')
def showJavaBuild():
    return render_template('build.html')


@app.route('/JavaBuild',methods=['POST'])
def JavaBuild():
 
    # read the posted values from the UI
	#_name = request.form['inputName']
	_git = request.form['inputRepo'] 

	builder = '<builders>\
		<org.jvnet.hudson.plugins.SbtPluginBuilder plugin="sbt@1.5">\
		<name>sbt</name>\
		<jvmFlags></jvmFlags>\
		<sbtFlags>-Dsbt.log.noformat=true</sbtFlags>\
		<actions></actions>\
		<subdirPath></subdirPath>\
		</org.jvnet.hudson.plugins.SbtPluginBuilder>\
		</builders>'

	git = 'https://github.com/TamerB/play-demo'
	git_name = '*/master'

	scm = '<scm class="hudson.plugins.git.GitSCM" plugin="git@2.4.4">\
		<configVersion>2</configVersion>\
		<userRemoteConfigs>\
		<hudson.plugins.git.UserRemoteConfig>\
		<url>' + git + '</url>\
		</hudson.plugins.git.UserRemoteConfig>\
		</userRemoteConfigs>\
		<branches>\
		<hudson.plugins.git.BranchSpec>\
		<name>' + git_name + '</name>\
		</hudson.plugins.git.BranchSpec>\
		</branches>\
		<doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>\
		<submoduleCfg class="list"/>\
		<extensions/>\
		</scm>'

	build = "<?xml version='1.0' encoding='UTF-8'?>\
		<project>\
		<actions/>\
		<description></description>\
		<keepDependencies>false</keepDependencies>\
		<properties/>\
		" + scm + "\
		<canRoam>true</canRoam>\
		<disabled>false</disabled>\
		<blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>\
		<blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>\
		<triggers/>\
		<concurrentBuild>false</concurrentBuild>\
		" + builder + "\
		<publishers/>\
		<buildWrappers/>\
		</project>"

	pName = str(_git[19:-4])
	pName = re.sub("/","-", pName)

	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	#server.delete_job(pName)
	server.create_job(pName, build)
	server.build_job(pName)
	
	#last_build_number = server.get_job_info(pName)['lastCompletedBuild']['number']
	#build_info = server.get_job_info(pName, last_build_number)
	#print last_build_number
	#print build_info
	#view_config = server.get_view_config(_name)
	#views = server.get_views()
	#print views

	#if _name and _email and _password:
	#	return json.dumps({'html':'<span>All fields good !!</span>'})
	#else:
	#	return json.dumps({'html':'<span>Enter the required fields</span>'})

#@app.route('/signUp')
#def signUp():
    # create user code will be here !!

if __name__ == "__main__":
    app.run()
    print 'hi'

