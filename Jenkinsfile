pipeline {
    agent any

    stages {
        stage('Get Code') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'py -m pip install flask pytest requests'
            }
        }

        stage('Unit') {
            steps {
                bat 'py -m pytest test\\unit --junitxml=unit-results.xml'
                junit 'unit-results.xml'
            }
        }

        stage('Start Wiremock (9090)') {
            steps {
                bat '''
                start /B java -jar tools\\wiremock\\wiremock.jar --port 9090 --root-dir tools\\wiremock
                '''
                sleep time: 2, unit: 'SECONDS'
            }
        }

        stage('Start API (5000)') {
            steps {
                bat '''
                set FLASK_APP=app.api:api_application
                start /B py -m flask run --host=127.0.0.1 --port=5000
                '''
                sleep time: 3, unit: 'SECONDS'
            }
        }

        stage('Rest') {
            steps {
                bat 'py -m pytest test\\rest --junitxml=rest-results.xml'
                junit 'rest-results.xml'
            }
        }
    }

    post {
        always {
            bat 'taskkill /F /IM python.exe || exit 0'
        }
    }
}
