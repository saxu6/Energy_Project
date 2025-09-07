// Enhanced Energy Consumption Analyzer - Frontend JavaScript

class EnergyAnalyzer {
    constructor() {
        this.currentTheme = 'light';
        this.analysisData = null;
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupFormHandlers();
        this.populateDayOptions();
        this.setupEventListeners();
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const html = document.documentElement;
        
        // Check for saved theme preference or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        themeToggle.addEventListener('click', () => {
            const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
        });
    }

    setTheme(theme) {
        const html = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('i');
        
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        
        if (theme === 'dark') {
            html.classList.add('dark');
            icon.className = 'fas fa-moon text-lg';
        } else {
            html.classList.remove('dark');
            icon.className = 'fas fa-sun text-lg';
        }
    }

    setupFormHandlers() {
        const form = document.getElementById('analysisForm');
        const monthSelect = document.getElementById('month');
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.runAnalysis();
        });
        
        // Update day options when month changes
        monthSelect.addEventListener('change', () => {
            this.populateDayOptions();
        });
    }

    populateDayOptions() {
        const monthSelect = document.getElementById('month');
        const daySelect = document.getElementById('day');
        const month = monthSelect.value;
        
        // Clear existing options
        daySelect.innerHTML = '';
        
        // Get number of days in selected month
        const daysInMonth = this.getDaysInMonth(month);
        
        // Add day options
        for (let day = 1; day <= daysInMonth; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day;
            daySelect.appendChild(option);
        }
    }

    getDaysInMonth(month) {
        const monthDays = {
            'January': 31, 'February': 29, 'March': 31, 'April': 30,
            'May': 31, 'June': 30, 'July': 31, 'August': 31,
            'September': 30, 'October': 31, 'November': 30, 'December': 31
        };
        return monthDays[month] || 31;
    }

    setupEventListeners() {
        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    async runAnalysis() {
        const formData = this.getFormData();
        
        // Show results section and loading state
        this.showResultsSection();
        this.showLoadingState();
        
        try {
            // Call actual API endpoint
            const result = await this.callAnalysisAPI(formData);
            this.analysisData = result;
            
            // Hide loading and show results
            this.hideLoadingState();
            this.displayResults(result);
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError('Analysis failed. Please try again.');
        }
    }

    getFormData() {
        const form = document.getElementById('analysisForm');
        const formData = new FormData(form);
        
        return {
            bedType: formData.get('bedType') || document.getElementById('bedType').value,
            month: formData.get('month') || document.getElementById('month').value,
            day: formData.get('day') || document.getElementById('day').value,
            analysisMode: formData.get('analysisMode') || 'basic',
            showAnomalies: document.getElementById('showAnomalies').checked,
            showTrends: document.getElementById('showTrends').checked
        };
    }

    async callAnalysisAPI(formData) {
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    generateMockData(formData) {
        const roomCount = 15;
        const rooms = [];
        
        // Generate room data
        for (let i = 1; i <= roomCount; i++) {
            const baseEnergy = 3 + Math.random() * 2; // 3-5 kWh base
            const isAnomaly = Math.random() < 0.2; // 20% chance of anomaly
            
            let energy = baseEnergy;
            if (isAnomaly) {
                energy += (Math.random() - 0.5) * 4; // Add/subtract up to 2 kWh
            }
            
            rooms.push({
                roomNo: i,
                energy: Math.max(0.5, energy), // Minimum 0.5 kWh
                isAnomaly: isAnomaly,
                anomalyType: isAnomaly ? this.getRandomAnomalyType() : 'Normal',
                confidence: isAnomaly ? 0.6 + Math.random() * 0.4 : 0.1 + Math.random() * 0.3
            });
        }
        
        // Calculate summary statistics
        const totalEnergy = rooms.reduce((sum, room) => sum + room.energy, 0);
        const anomalies = rooms.filter(room => room.isAnomaly);
        const avgConfidence = anomalies.length > 0 ? 
            anomalies.reduce((sum, room) => sum + room.confidence, 0) / anomalies.length : 0;
        
        return {
            summary: {
                totalRooms: roomCount,
                totalEnergy: totalEnergy,
                avgEnergy: totalEnergy / roomCount,
                anomalyCount: anomalies.length,
                anomalyPercentage: (anomalies.length / roomCount) * 100,
                avgConfidence: avgConfidence
            },
            rooms: rooms,
            anomalies: {
                highConsumption: anomalies.filter(a => a.anomalyType === 'High Consumption').length,
                lowConsumption: anomalies.filter(a => a.anomalyType === 'Low Consumption').length,
                unusualPattern: anomalies.filter(a => a.anomalyType === 'Unusual Pattern').length
            },
            patterns: {
                peakHoursAvg: 1.2 + Math.random() * 0.8,
                morningUsageAvg: 0.8 + Math.random() * 0.6,
                nightUsageAvg: 0.5 + Math.random() * 0.4,
                mostEfficientRoom: Math.floor(Math.random() * roomCount) + 1,
                leastEfficientRoom: Math.floor(Math.random() * roomCount) + 1,
                usageConsistency: 0.6 + Math.random() * 0.3
            },
            deepLearningInsights: formData.analysisMode === 'enhanced' ? {
                lstm: {
                    avgAnomalyScore: 0.3 + Math.random() * 0.4,
                    highConfidenceAnomalies: Math.floor(Math.random() * 5)
                },
                autoencoder: {
                    avgReconstructionError: 0.1 + Math.random() * 0.2,
                    highErrorInstances: Math.floor(Math.random() * 8)
                },
                transformer: {
                    avgAnomalyScore: 0.4 + Math.random() * 0.3,
                    highConfidenceAnomalies: Math.floor(Math.random() * 6)
                }
            } : null,
            recommendations: this.generateRecommendations(anomalies.length, totalEnergy / roomCount)
        };
    }

    getRandomAnomalyType() {
        const types = ['High Consumption', 'Low Consumption', 'Unusual Pattern'];
        return types[Math.floor(Math.random() * types.length)];
    }

    generateRecommendations(anomalyCount, avgEnergy) {
        const recommendations = [];
        
        if (anomalyCount > 3) {
            recommendations.push("High anomaly rate detected. Consider investigating equipment or occupancy patterns.");
        }
        
        if (avgEnergy > 4) {
            recommendations.push("Above-average energy consumption. Implement energy efficiency measures.");
        }
        
        if (anomalyCount === 0) {
            recommendations.push("No anomalies detected. System is operating normally.");
        }
        
        recommendations.push("Monitor peak hours usage to optimize energy distribution.");
        recommendations.push("Consider implementing smart metering for real-time monitoring.");
        
        return recommendations;
    }

    showResultsSection() {
        const resultsSection = document.getElementById('results');
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    showLoadingState() {
        document.getElementById('loadingState').classList.remove('hidden');
        document.getElementById('resultsContent').classList.add('hidden');
    }

    hideLoadingState() {
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('resultsContent').classList.remove('hidden');
    }

    displayResults(data) {
        // Handle API response format
        if (data.success && data.data) {
            // Convert API data to frontend format
            const rooms = data.data.map(room => ({
                roomNo: room['Room No'],
                energy: room['Total Energy (kWh)'],
                isAnomaly: room.final_anomaly === 1,
                anomalyType: room.anomaly_type,
                confidence: room.anomaly_confidence
            }));
            
            const summary = data.summary;
            const anomalies = {
                highConsumption: data.insights.anomalies.high_consumption || 0,
                lowConsumption: data.insights.anomalies.low_consumption || 0,
                unusualPattern: data.insights.anomalies.unusual_pattern || 0
            };
            
            const recommendations = data.insights.recommendations || [];
            
            this.updateSummaryCards(summary);
            this.createCharts({ rooms, anomalies });
            this.displayRecommendations(recommendations);
        } else {
            throw new Error('Invalid data format received from API');
        }
    }

    updateSummaryCards(summary) {
        document.getElementById('totalRooms').textContent = summary.total_rooms || summary.totalRooms;
        document.getElementById('totalEnergy').textContent = `${(summary.total_energy || summary.totalEnergy).toFixed(1)} kWh`;
        document.getElementById('anomalyCount').textContent = summary.anomaly_count || summary.anomalyCount;
        document.getElementById('avgConfidence').textContent = `${(summary.anomaly_percentage || 0).toFixed(1)}%`;
    }

    createCharts(data) {
        this.createMainChart(data.rooms);
        this.createAnomalyChart(data.anomalies);
    }

    createMainChart(rooms) {
        const roomNumbers = rooms.map(room => room.roomNo);
        const energyValues = rooms.map(room => room.energy);
        const colors = rooms.map(room => room.isAnomaly ? '#ef4444' : '#3b82f6');
        
        const trace = {
            x: roomNumbers,
            y: energyValues,
            type: 'bar',
            marker: {
                color: colors,
                line: {
                    color: this.currentTheme === 'dark' ? '#374151' : '#e5e7eb',
                    width: 1
                }
            },
            name: 'Energy Consumption'
        };
        
        const layout = {
            title: {
                text: 'Energy Consumption by Room',
                font: {
                    color: this.currentTheme === 'dark' ? '#ffffff' : '#000000'
                }
            },
            xaxis: {
                title: 'Room Number',
                color: this.currentTheme === 'dark' ? '#ffffff' : '#000000',
                gridcolor: this.currentTheme === 'dark' ? '#374151' : '#e5e7eb'
            },
            yaxis: {
                title: 'Energy (kWh)',
                color: this.currentTheme === 'dark' ? '#ffffff' : '#000000',
                gridcolor: this.currentTheme === 'dark' ? '#374151' : '#e5e7eb'
            },
            plot_bgcolor: this.currentTheme === 'dark' ? '#1f2937' : '#ffffff',
            paper_bgcolor: this.currentTheme === 'dark' ? '#1f2937' : '#ffffff',
            showlegend: false
        };
        
        Plotly.newPlot('mainChart', [trace], layout, {responsive: true});
    }

    createAnomalyChart(anomalies) {
        const labels = ['High Consumption', 'Low Consumption', 'Unusual Pattern'];
        const values = [
            anomalies.highConsumption,
            anomalies.lowConsumption,
            anomalies.unusualPattern
        ];
        const colors = ['#ef4444', '#3b82f6', '#f59e0b'];
        
        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            marker: {
                colors: colors
            },
            textinfo: 'label+percent',
            textposition: 'outside'
        };
        
        const layout = {
            title: {
                text: 'Anomaly Distribution',
                font: {
                    color: this.currentTheme === 'dark' ? '#ffffff' : '#000000'
                }
            },
            plot_bgcolor: this.currentTheme === 'dark' ? '#1f2937' : '#ffffff',
            paper_bgcolor: this.currentTheme === 'dark' ? '#1f2937' : '#ffffff'
        };
        
        Plotly.newPlot('anomalyChart', [trace], layout, {responsive: true});
    }

    displayDeepLearningInsights(insights) {
        const container = document.getElementById('deepLearningInsights');
        const content = document.getElementById('dlInsightsContent');
        
        if (!insights) {
            container.classList.add('hidden');
            return;
        }
        
        container.classList.remove('hidden');
        content.innerHTML = '';
        
        Object.entries(insights).forEach(([model, data]) => {
            const card = document.createElement('div');
            card.className = 'bg-gray-50 dark:bg-gray-700 rounded-lg p-4';
            
            const modelName = model.toUpperCase();
            const icon = this.getModelIcon(model);
            
            card.innerHTML = `
                <div class="flex items-center mb-3">
                    <i class="${icon} text-lg mr-2 text-purple-600 dark:text-purple-400"></i>
                    <h4 class="font-semibold text-gray-900 dark:text-white">${modelName}</h4>
                </div>
                <div class="space-y-2">
                    ${Object.entries(data).map(([key, value]) => `
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600 dark:text-gray-400">${this.formatKey(key)}:</span>
                            <span class="text-sm font-medium text-gray-900 dark:text-white">
                                ${typeof value === 'number' ? value.toFixed(3) : value}
                            </span>
                        </div>
                    `).join('')}
                </div>
            `;
            
            content.appendChild(card);
        });
    }

    getModelIcon(model) {
        const icons = {
            lstm: 'fas fa-brain',
            autoencoder: 'fas fa-compress-arrows-alt',
            transformer: 'fas fa-bolt'
        };
        return icons[model] || 'fas fa-cog';
    }

    formatKey(key) {
        return key.replace(/([A-Z])/g, ' $1')
                 .replace(/^./, str => str.toUpperCase());
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendationsList');
        container.innerHTML = '';
        
        recommendations.forEach((rec, index) => {
            const item = document.createElement('div');
            item.className = 'flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg';
            
            item.innerHTML = `
                <i class="fas fa-lightbulb text-yellow-600 dark:text-yellow-400 mt-1"></i>
                <span class="text-gray-700 dark:text-gray-300">${rec}</span>
            `;
            
            container.appendChild(item);
        });
    }

    showError(message) {
        this.hideLoadingState();
        
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Global functions
function scrollToAnalysis() {
    const analysisSection = document.getElementById('analysis');
    analysisSection.scrollIntoView({ behavior: 'smooth' });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.energyAnalyzer = new EnergyAnalyzer();
});

// Handle window resize for responsive charts
window.addEventListener('resize', () => {
    if (window.energyAnalyzer && window.energyAnalyzer.analysisData) {
        window.energyAnalyzer.createCharts(window.energyAnalyzer.analysisData);
    }
});
