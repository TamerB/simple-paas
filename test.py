#import os

#os.system("echo 'jenkins.model.Jenkins.instance.securityRealm.createAccount(\"user1\", \"password123\")' | java -jar jenkins-cli.jar -s http://localhost:8090/ groovy =")