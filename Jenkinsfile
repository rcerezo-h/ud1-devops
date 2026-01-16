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

    stage('Start Services (win)') {
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

        // Limpieza previa por si quedaron procesos de builds anteriores ocupando puertos
        bat '''
@echo off
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >NUL 2>NUL
for /f "tokens=5" %%a in ('netstat -aon ^| find ":9090" ^| find "LISTENING"') do taskkill /F /PID %%a >NUL 2>NUL
exit /b 0
'''

        bat "start /B java -jar tools\\wiremock\\wiremock.jar --port 9090 --root-dir tools\\wiremock"
        bat "set FLASK_APP=app.api:api_application && start \"flask\" /B \"%PYTHON%\" -m flask run --host=127.0.0.1 --port=5000"

        // Espera real (con reintentos) a que ambos servicios respondan
        retry(8) {
          sleep time: 2, unit: 'SECONDS'
          bat '''
echo Probando WireMock...
powershell -Command "try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:9090/__admin).StatusCode } catch { exit 1 }"
echo Probando Flask...
powershell -Command "try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/).StatusCode } catch { exit 1 }"
'''
        }
      }
    }

    stage('Parallel Analysis & Tests') {
      parallel {

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

        stage('Flake8 (agente2)') {
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

        stage('Bandit (agente2)') {
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

        stage('Performance (JMeter) (win)') {
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
            bat "\"%JMETER%\" -n -t test\\jmeter\\test-plan.jmx -l test\\jmeter\\results.jtl"
          }
        }
      }
    }

    // REST fuera del paralelo
    stage('Rest (win)') {
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
        bat "\"%PYTHON%\" -m pytest test\\rest --junitxml=rest-results.xml"
        junit 'rest-results.xml'
      }
    }
  }

  post {
    always {
      node('win') {
        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
          recordCoverage tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']]
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
          recordIssues tools: [flake8(pattern: 'flake8-report.txt')]
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
          perfReport sourceDataFiles: 'test\\jmeter\\results.jtl'
        }

        archiveArtifacts artifacts: 'test\\jmeter\\results.jtl, coverage.xml, flake8-report.txt, bandit-report.json, unit-results.xml, rest-results.xml',
                         allowEmptyArchive: true

        // Limpieza al final
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
