pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "2004gautam/devopsproject"
        DOCKER_TAG   = "${env.BUILD_NUMBER}"
        K8S_NAMESPACE = "default"
    }

    stages {

        // ========================
        // Stage 1: Checkout Source
        // ========================
        stage('Checkout') {
            steps {
                echo "🔄 Checking out source code..."
                checkout scm
            }
        }

        // ========================
        // Stage 2: Build Docker Image
        // ========================
        stage('Build Docker') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dock-id-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                    echo Logging into Docker Hub...
                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin

                    echo Building Docker image...
                    docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% .
                    docker tag %DOCKER_IMAGE%:%DOCKER_TAG% %DOCKER_IMAGE%:latest
                    """
                }
            }
        }

        // ========================
        // Stage 3: Test Docker Container
        // ========================
        stage('Test Application') {
            steps {
                script {
                    echo "⚡ Testing Docker container..."
                    
                    // Remove old container safely
                    bat "docker rm -f test-app || echo No existing container"

                    // Run container
                    bat "docker run -d --name test-app -p 5000:5000 %DOCKER_IMAGE%:%DOCKER_TAG%"

                    // Wait for app startup
                    bat "ping 127.0.0.1 -n 10 >nul"

                    // Health check using PowerShell
                    def health = powershell(returnStdout: true, script: """
                        try {
                            \$status = (Invoke-WebRequest http://localhost:5000/health -UseBasicParsing).StatusCode
                            Write-Output \$status
                        } catch {
                            Write-Output "FAIL"
                        }
                    """).trim()

                    if (health != '200') {
                        error("❌ Health check failed! Response: ${health}")
                    }

                    // Stop and remove container
                    bat "docker stop test-app && docker rm test-app"
                }
            }
        }

        // ========================
        // Stage 4: Push Docker Image
        // ========================
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dock-id-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                    echo Pushing Docker images...
                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                    docker push %DOCKER_IMAGE%:%DOCKER_TAG%
                    docker push %DOCKER_IMAGE%:latest
                    """
                }
            }
        }

        // ========================
        // Stage 5: Deploy to Kubernetes
        // ========================
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-cred', variable: 'KUBECONFIG_FILE')]) {
                    bat """
                    echo Setting up kubeconfig...
                    if not exist "%USERPROFILE%\\.kube" mkdir "%USERPROFILE%\\.kube"
                    copy /Y "%KUBECONFIG_FILE%" "%USERPROFILE%\\.kube\\config"

                    echo Applying Kubernetes manifests...
                    kubectl apply -f k8s\\deployment.yaml --namespace %K8S_NAMESPACE% --validate=false
                    kubectl apply -f k8s\\service.yaml --namespace %K8S_NAMESPACE% --validate=false

                    echo Updating deployment image...
                    kubectl set image deployment/ticket-booking-deployment ticket-booking-container=%DOCKER_IMAGE%:%DOCKER_TAG% --namespace %K8S_NAMESPACE%

                    echo Waiting for rollout to complete...
                    kubectl rollout status deployment/ticket-booking-deployment --namespace %K8S_NAMESPACE% --timeout=120s
                    """
                }
            }
        }
    }

    // ========================
    // Post Actions
    // ========================
    post {
        success {
            echo "✅ SUCCESS: Build ${env.BUILD_NUMBER} completed."
        }
        failure {
            echo "❌ FAILED: Build ${env.BUILD_NUMBER}."
        }
        always {
            echo "🧹 Cleaning up Docker images..."
            bat "docker image prune -f"
        }
    }
}
