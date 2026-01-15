pipeline {
  agent any

  environment {
    PYTHON = 'C:\\Users\\tmt-1\\AppData\\Local\\Python\\bin\\python.exe'
    JMETER = 'C:\\jmeter\\bin\\jmeter.bat'
  }

  stages {

    stage('Get Code') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        bat "\"%PYTHON%\" -m pip install --upgrade pip"
        bat "\"%PYTHON%\" -m pip install flask pytest requests pytest-cov flake8 bandit"
      }
    }

    stage('Unit + Coverage') {
      steps {
        bat """
        \"%PYTHON%\" -m pytest test\\unit ^
          --junitxml=unit-results.xml ^
          --cov=app ^
          --cov-report=xml:coverage.xml
        """
        junit 'unit-results.xml'
      }
    }

    stage('Static Analysis (Flake8)') {
      steps {
        bat """
        \"%PYTHON%\" -m flake8 . --format=pylint --output-file=flake8-report.txt || exit /b 0
        """
      }
    }

    stage('Security Scan (Bandit)') {
      steps {
        // Bandit en SARIF (para Warnings-NG)
        bat """
        \"%PYTHON%\" -m bandit -r . -f sarif -o bandit-report.sarif || exit /b 0
        """
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
        bat "set FLASK_APP=app.api:api_application && start \"flask\" /B \"%PYTHON%\" -m flask run --host=127.0.0.1 --port=5000"
        sleep time: 5, unit: 'SECONDS'
      }
    }

    stage('Rest') {
      steps {
        bat "\"%PYTHON%\" -m pytest test\\rest --junitxml=rest-results.xml"
        junit 'rest-results.xml'
      }
    }

    stage('Performance (JMeter)') {
      steps {
        bat "\"%JMETER%\" -n -t test\\jmeter\\test-plan.jmx -l test\\jmeter\\results.jtl"
      }
    }
  }

  post {
    always {
      // --- Publicación Coverage ---
      recordCoverage tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']]

      // --- Publicación Warnings NG ---
      // Flake8
      recordIssues tools: [flake8(pattern: 'flake8-report.txt')]
      // Bandit (SARIF)
      recordIssues tools: [sarif(pattern: 'bandit-report.sarif')]

      // --- Performance ---
      perfReport sourceDataFiles: 'test\\jmeter\\results.jtl'

      // --- Archivos ---
      archiveArtifacts artifacts: 'test\\jmeter\\results.jtl, coverage.xml, flake8-report.txt, bandit-report.sarif, unit-results.xml, rest-results.xml', allowEmptyArchive: false

      // --- Limpieza procesos ---
      bat '''
@echo off
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >NUL 2>NUL
for /f "tokens=5" %%a in ('netstat -aon ^| find ":9090" ^| find "LISTENING"') do taskkill /F /PID %%a >NUL 2>NUL
exit /b 0
'''
    }
  }
}
