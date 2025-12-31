pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
        AWS_DEFAULT_REGION    = 'ap-south-1'
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
                  -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
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
