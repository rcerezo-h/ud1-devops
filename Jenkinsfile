pipeline {
  agent none

  environment {
    PYTHON = 'C:\\Users\\tmt-1\\AppData\\Local\\Python\\bin\\python.exe'
    JMETER = 'C:\\jmeter\\bin\\jmeter.bat'
  }

  stages {

    stage('Get Code (win)') {
      agent { label 'win' }
      steps {
        bat '''
echo ===== INFO Agente =====
whoami
hostname
cd
echo ======================
'''
        checkout scm
      }
    }

    stage('Install Dependencies (agente1)') {
      agent { label 'agente1' }
      steps {
        bat '''
echo ===== INFO Agente =====
whoami
hostname
cd
echo ======================
'''
        checkout scm
        bat "\"%PYTHON%\" -m pip install --upgrade pip"
        bat "\"%PYTHON%\" -m pip install flask pytest requests pytest-cov flake8 bandit"
      }
    }

    stage('Unit + Coverage (agente1)') {
      agent { label 'agente1' }
      steps {
        bat '''
echo ===== INFO Agente =====
whoami
hostname
cd
echo ======================
'''
        checkout scm
        bat """
        \"%PYTHON%\" -m pytest test\\unit ^
          --junitxml=unit-results.xml ^
          --cov=app ^
          --cov-report=xml:coverage.xml
        """
        junit 'unit-results.xml'
      }
    }

    stage('Static Analysis (Flake8) (agente2)') {
      agent { label 'agente2' }
      steps {
        bat '''
echo ===== INFO Agente =====
whoami
hostname
cd
echo ======================
'''
        checkout scm
        bat "\"%PYTHON%\" -m flake8 . --format=pylint --output-file=flake8-report.txt || exit /b 0"
      }
    }

    stage('Security Scan (Bandit) (agente2)') {
      agent { label 'agente2' }
      steps {
        bat '''
echo ===== INFO Agente =====
whoami
hostname
cd
echo ======================
'''
        checkout scm
        bat "\"%PYTHON%\" -m bandit -r . -f json -o bandit-report.json || exit /b 0"
      }
    }

    stage('Start Services + Rest + Performance (win)') {
      agent { label 'win' }
      steps {
        bat '''
echo ===== INFO Agente =====
whoami
hostname
cd
echo ======================
'''
        checkout scm

        // Wiremock
        bat "start /B java -jar tools\\wiremock\\wiremock.jar --port 9090 --root-dir tools\\wiremock"
        sleep time: 2, unit: 'SECONDS'

        // API Flask
        bat "set FLASK_APP=app.api:api_application && start \"flask\" /B \"%PYTHON%\" -m flask run --host=127.0.0.1 --port=5000"
        sleep time: 5, unit: 'SECONDS'

        // Rest tests
        bat "\"%PYTHON%\" -m pytest test\\rest --junitxml=rest-results.xml"
        junit 'rest-results.xml'

        // Performance
        bat "\"%JMETER%\" -n -t test\\jmeter\\test-plan.jmx -l test\\jmeter\\results.jtl"
      }
    }
  }

  post {
    always {
      // Publicaciones y archivado
      node('win') {
        recordCoverage tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']]
        recordIssues tools: [flake8(pattern: 'flake8-report.txt')]
        perfReport sourceDataFiles: 'test\\jmeter\\results.jtl'

        archiveArtifacts artifacts: 'test\\jmeter\\results.jtl, coverage.xml, flake8-report.txt, bandit-report.json, unit-results.xml, rest-results.xml', allowEmptyArchive: false

        // Limpieza de procesos
        bat '''
@echo off
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >NUL 2>NUL
for /f "tokens=5" %%a in ('netstat -aon ^| find ":9090" ^| find "LISTENING"') do taskkill /F /PID %%a >NUL 2>NUL
exit /b 0
'''
      }
    }
  }
}
