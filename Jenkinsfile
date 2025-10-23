pipeline {
    agent any

    environment {
        DOCKER_USER = '2004gautam'
        DOCKER_PASS = credentials('docker-hub-pass') // Jenkins secret
        KUBECONFIG_FILE = credentials('kubeconfig-file') // Jenkins secret file
        IMAGE_NAME = '2004gautam/devopsproject'
        IMAGE_TAG  = '5'
    }

    stages {
        stage('Checkout Source') {
            steps {
                echo "🔄 Checking out source code..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat """
                echo Building Docker image...
                docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                docker tag %IMAGE_NAME%:%IMAGE_TAG% %IMAGE_NAME%:latest
                """
            }
        }

        stage('Test Docker Container') {
            steps {
                bat """
                echo ⚡ Testing Docker container...
                docker rm -f test-app || echo No existing container
                docker run -d --name test-app -p 5000:5000 %IMAGE_NAME%:%IMAGE_TAG%
                ping 127.0.0.1 -n 10 > nul
                powershell -Command "(Invoke-WebRequest http://localhost:5000/health).StatusCode"
                powershell -Command "(Invoke-WebRequest http://localhost:5000/).StatusCode"
                docker stop test-app && docker rm test-app
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-pass', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    bat """
                    echo Logging into Docker Hub...
                    echo %PASS% | docker login -u %USER% --password-stdin

                    echo Pushing Docker images...
                    docker push %IMAGE_NAME%:%IMAGE_TAG%
                    docker push %IMAGE_NAME%:latest
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                    bat """
                    echo Setting up kubeconfig...
                    if not exist "%USERPROFILE%\\.kube" mkdir "%USERPROFILE%\\.kube"
                    copy /Y "%KUBECONFIG_FILE%" "%USERPROFILE%\\.kube\\config"

                    echo Applying Kubernetes manifests...
                    kubectl apply -f k8s\\deployment.yaml --namespace default --validate=false
                    kubectl apply -f k8s\\service.yaml --namespace default --validate=false

                    echo Updating deployment image...
                    kubectl set image deployment/ticket-booking-deployment ticket-booking-container=%IMAGE_NAME%:%IMAGE_TAG% --namespace default

                    echo Checking rollout status...
                    kubectl rollout status deployment/ticket-booking-deployment --namespace default --timeout=120s
                    """
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker images..."
            bat 'docker image prune -f'
        }
        success {
            echo "✅ Pipeline succeeded!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
