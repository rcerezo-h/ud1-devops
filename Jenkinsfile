pipeline {
  agent any

  environment {
    PYTHON = 'C:\\Users\\tmt-1\\AppData\\Local\\Python\\bin\\python.exe'
  }

  stages {
    stage('Get Code') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        bat "\"%PYTHON%\" -m pip install flask pytest requests"
      }
    }

    stage('Unit') {
      steps {
        bat "\"%PYTHON%\" -m pytest test\\unit --junitxml=unit-results.xml"
        junit 'unit-results.xml'
      }
    }

    stage('Start Wiremock (9090)') {
      steps {
        bat "start /B java -jar tools\\wiremock\\wiremock.jar --port 9090 --root-dir tools\\wiremock"
        sleep time: 2, unit: 'SECONDS'
      }
    }

    stage('Start API (5000)') {
      steps {
        bat "set FLASK_APP=app.api:api_application&& start /B \"%PYTHON%\" -m flask run --host=127.0.0.1 --port=5000"
        sleep time: 3, unit: 'SECONDS'
      }
    }

    stage('Rest') {
      steps {
        bat "\"%PYTHON%\" -m pytest test\\rest --junitxml=rest-results.xml"
        junit 'rest-results.xml'
      }
    }
  }

  post {
    always {
      bat "for /f \"tokens=5\" %%%%a in ('netstat -aon ^| find \":5000\" ^| find \"LISTENING\"') do taskkill /F /PID %%%%a"
      bat "for /f \"tokens=5\" %%%%a in ('netstat -aon ^| find \":9090\" ^| find \"LISTENING\"') do taskkill /F /PID %%%%a"
    }
  }
}
