import os
import jenkins
import re
import json 
import sys
import urllib2
import time
import glob

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

#app.secret_key = "my precious"

@app.route("/")
def main(server):
	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	jobs = server.get_jobs()
	jobStatus={}
	for j in jobs:
		jobStatus[j["fullname"]]=getLastBuildStatus(str(j["fullname"]))
	return render_template('index.html', jobs=jobs, jobStatus = jobStatus)

#@app.route('/login', methods['GET', 'POST'])
#def login():
#	error = None
#	if request.method == 'POST':
#		try:
#			server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
#			session['logged_in'] = True
#			return redirct(url_for('home'))
#		except:
#			error = 'Invalid credentials. Please try again'
#			return render_template('login.html', error = error)


#@app.route('/logout')
#def logtou():
#	session.pop('logged_in', None)
#	return redirect(url_for('welcome'))

#def server(user, password):
#	try:
#		server = jenkins.Jenkins('http://localhost:8090', username = user, password = password)
#		return redircet('index.html', server = server)
#	except:
#		return redircet('login.html', )

@app.route('/showJob/<job>')
def showJob(job):
	#jobStatus = {}
	#x=1
	print "start"
	#iterator = True

	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	try:
		last_build_number = server.get_job_info(job)['lastBuild']['number']
		print last_build_number
	except:
		last_build_number = 0

	jobStatus = getJobLastBuildStatus(job, last_build_number)
	
	return render_template('job.html', job = job, jobStatus = jobStatus)

@app.route('/showJavaBuild')
def showJavaBuild():
    return render_template('build.html')

@app.route('/showMavenSpringBuild')
def showMavenSpringBuild():
	return render_template('mavenBuild.html')

@app.route('/job/<pName>/<bNum>/stop')
def delBuild(pName, bNum):
	print "delBuild"
	os.system("java -jar jenkins-cli.jar -s http://localhost:8090/ delete-builds " + pName + " '" + bNum + "' --username TamerB --password tamer")
	return redirect('/showJob/' + pName)

def mavenXmlGen(pName, git):
	build = "<?xml version='1.0' encoding='UTF-8'?>\
	<maven2-moduleset plugin='maven-plugin@2.7.1'>\
	<actions/>\
	<description></description>\
	<keepDependencies>false</keepDependencies>\
	<properties/>\
	<scm class='hudson.plugins.git.GitSCM' plugin='git@2.4.4'>\
	<configVersion>2</configVersion>\
	<userRemoteConfigs>\
	<hudson.plugins.git.UserRemoteConfig>\
	<url>" + git + "</url>\
	</hudson.plugins.git.UserRemoteConfig>\
	</userRemoteConfigs>\
	<branches>\
	<hudson.plugins.git.BranchSpec>\
	<name>*/master</name>\
	</hudson.plugins.git.BranchSpec>\
	</branches>\
	<doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>\
	<submoduleCfg class='list'/>\
	<extensions/>\
	</scm>\
	<canRoam>true</canRoam>\
	<disabled>false</disabled>\
	<blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>\
	<blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>\
	<triggers/>\
	<concurrentBuild>false</concurrentBuild>\
	<rootModule>\
	<groupId>com.mkyong</groupId>\
	<artifactId>" + pName + "</artifactId>\
	</rootModule>\
	<aggregatorStyleBuild>true</aggregatorStyleBuild>\
	<incrementalBuild>false</incrementalBuild>\
	<ignoreUpstremChanges>false</ignoreUpstremChanges>\
	<archivingDisabled>false</archivingDisabled>\
	<siteArchivingDisabled>false</siteArchivingDisabled>\
	<fingerprintingDisabled>false</fingerprintingDisabled>\
	<resolveDependencies>false</resolveDependencies>\
	<processPlugins>false</processPlugins>\
	<mavenValidationLevel>-1</mavenValidationLevel>\
	<runHeadless>false</runHeadless>\
	<disableTriggerDownstreamProjects>false</disableTriggerDownstreamProjects>\
	<blockTriggerWhenBuilding>true</blockTriggerWhenBuilding>\
	<settings class='jenkins.mvn.DefaultSettingsProvider'/>\
	<globalSettings class='jenkins.mvn.DefaultGlobalSettingsProvider'/>\
	<reporters/>\
	<publishers/>\
	<buildWrappers/>\
	<prebuilders/>\
	<postbuilders>\
	<hudson.tasks.Shell>\
	<command>mvn package\
	</command>\
	</hudson.tasks.Shell>\
	</postbuilders>\
	<runPostStepsIfResult>\
	<name>FAILURE</name>\
	<ordinal>2</ordinal>\
	<color>RED</color>\
	<completeBuild>true</completeBuild>\
	</runPostStepsIfResult>\
	</maven2-moduleset>"

	return build


def xmlGen(pName, git):
	builder = '<builders>\
		<org.jvnet.hudson.plugins.SbtPluginBuilder plugin="sbt@1.5">\
		<name>sbt</name>\
		<jvmFlags></jvmFlags>\
		<sbtFlags>-Dsbt.log.noformat=true</sbtFlags>\
		<actions>test</actions>\
		<subdirPath></subdirPath>\
		</org.jvnet.hudson.plugins.SbtPluginBuilder>\
		<hudson.tasks.Shell>\
		<command>activator debian:packageBin</command>\
		</hudson.tasks.Shell>\
		</builders>'

	publisher = '<publishers>\
		<hudson.plugins.deploy.DeployPublisher plugin="deploy@1.10">\
		<contextPath>' + pName + '</contextPath>\
		<war>*.war</war>\
		<onFailure>false</onFailure>\
		</hudson.plugins.deploy.DeployPublisher>\
		</publishers>'

	#git = 'https://github.com/TamerB/play-demo'
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
		" + builder + publisher + "\
		<buildWrappers/>\
		</project>"

	return build

def getLastBuildStatus(pName):

	jenkinsUrl = "http://localhost:8090/job/"
	
	try:
		jenkinsStream = urllib2.urlopen( jenkinsUrl + pName + "/lastBuild/api/json" )
	except urllib2.HTTPError, e:
		return "No builds"

	try:
		buildStatusJson = json.load(jenkinsStream)
		if buildStatusJson.has_key("result"):
			return buildStatusJson["result"]
	except:
		return "No builds"

def getLastBuildStatusContinous(pName):
	jenkinsUrl = "http://localhost:8090/job/"
	
	while True:
		time.sleep(5)
		try:
			jenkinsStream = urllib2.urlopen( jenkinsUrl + pName + "/lastBuild/api/json" )
		except urllib2.HTTPError, e:
			continue

		try:
			buildStatusJson = json.load(jenkinsStream)
			if buildStatusJson.has_key("result"):
				if buildStatusJson["result"] == "SUCCESS" or buildStatusJson["result"] == "FAILURE" or buildStatusJson[
				"result"]=="ABORTED":
					print buildStatusJson["result"]
					return buildStatusJson["result"]
		except:
			continue

def getJobLastBuildStatus(pName, build):

	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	try:
		return server.get_build_console_output(pName, build)
	except urllib2.HTTPError, e:
		return "Not Built Yet"
		

def createJob(pName, build):
	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	server.create_job(pName, build)
	buildJob(pName)


def buildJob(pName):
	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	server.build_job(pName)
	return getLastBuildStatus(pName)

@app.route('/job/<pName>/delete')
def deleteJob(pName):
	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	server.delete_job(pName)
	return redirect("/")

def stopBuild(pName, bNum):
	os.system("java -jar jenkins-cli.jar -s http://localhost:8080/ delete-builds " + pName + " '" + bNum + "' --username TamerB --password tamer")

@app.route('/MavenSpringBuild', methods=['POST'])
def MavenSpringBuild():
	_git = request.form['inputRepo']
	pName = str(_git[19:-4])
	pName = re.sub("/","_",pName)

	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	server.create_job(pName, mavenXmlGen(pName, _git))
	server.build_job(pName)
	getLastBuildStatusContinous(pName)
	warArr = glob.glob('/var/lib/jenkins/jobs/' + pName + '/workspace/target/*.war')
	warFile = re.sub("/","-", warArr[0])
	print warFile
	#os.system("echo ay 7aga")
	ip = str(os.system("curl localhost:6666/subscribe/" + pName + "/" + warFile))
	print ip
	return ip
	#return "Success"

@app.route('/JavaBuild',methods=['POST'])
def JavaBuild():
 
	_git = request.form['inputRepo']

	# Job Name
	pName = str(_git[19:-4])
	pName = re.sub("/","_", pName)

	# Login to jenkins
	server = jenkins.Jenkins('http://localhost:8090', username = 'TamerB', password = 'tamer')
	#server = jenkins.Jenkins('http://ec2-52-90-194-22.compute-1.amazonaws.com/jenkins/', username = 'user', password = 'Wosh2TgPiHmz')
	server.create_job(pName, xmlGen(pName, _git))
	server.build_job(pName)
	#print 'done 2'
	getLastBuildStatusContinous(pName)
	return "Success"
	#return redirect('/showJob/' + pName)
	#return redirect('/showJob/' + pName)
	#return getLastBuildStatus(pName)

if __name__ == "__main__":
    app.run()
    print 'hi'


