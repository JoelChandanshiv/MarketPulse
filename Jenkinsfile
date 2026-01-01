pipeline {
    agent any

    
    parameters {
        string(name: 'YEAR',  defaultValue: '', description: 'Data year (YYYY)')
        string(name: 'MONTH', defaultValue: '', description: 'Data month (MM)')
        string(name: 'DAY',   defaultValue: '', description: 'Data day (DD)')
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws_access_key')
        AWS_SECRET_ACCESS_KEY = credentials('aws_secret_key')
    }

    stages {

        stage('Validate Workspace') {
            steps {
                sh 'ls -la'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t real-time-risk-platform .'
            }
        }

        stage('Run Risk Pipeline') {
            steps {
                sh '''
                docker run --rm \
                  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
                  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
                  -e YEAR=${YEAR} \
                  -e MONTH=${MONTH} \
                  -e DAY=${DAY} \
                  real-time-risk-platform
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline executed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
