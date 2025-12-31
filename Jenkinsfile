pipeline {
    agent any

    environment {
        IMAGE_NAME = "real-time-risk-platform"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/JoelChandanshiv/real-time-risk-platform.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Run Risk Pipeline') {
            steps {
                sh 'docker run --rm $IMAGE_NAME'
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
