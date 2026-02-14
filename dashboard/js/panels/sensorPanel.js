/**
 * Sensor Panel
 * Displays real-time sensor readings
 * Dynamically created for each active sensor plugin
 */

class SensorPanel extends BasePanel {
    constructor(panelId, config) {
        super(panelId, config);
        this.panelType = 'sensor';
        this.sensorName = config.sensorName || 'Unknown';
        this.sensorType = config.sensorType || 'generic';
        this.value = config.value || 0;
        this.history = [];
        this.maxHistorySize = 50;
        this.minValue = null;
        this.maxValue = null;
    }

    getTitle() {
        return `📡 ${this.formatName(this.sensorName)}`;
    }

    getContentHTML() {
        return `
            <div class="sensor-content">
                <div class="sensor-reading">
                    <div class="reading-label">${this.sensorType}</div>
                    <div class="reading-value">--</div>
                    <div class="reading-unit">${this.getUnitForType(this.sensorType)}</div>
                </div>
                <div class="sensor-stats">
                    <div class="stat">
                        <span class="stat-label">Min:</span>
                        <span class="stat-value">--</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Max:</span>
                        <span class="stat-value">--</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Avg:</span>
                        <span class="stat-value">--</span>
                    </div>
                </div>
                <div class="sensor-chart">
                    <canvas class="sensor-sparkline"></canvas>
                </div>
            </div>
        `;
    }

    onRender() {
        this.canvas = this.element.querySelector('.sensor-sparkline');
        this.setupChart();
    }

    onUpdate(event) {
        const { value, timestamp } = event.data;
        this.value = value;

        // Track history
        this.history.unshift({ value, timestamp });
        if (this.history.length > this.maxHistorySize) {
            this.history.pop();
        }

        // Update min/max
        if (this.minValue === null || value < this.minValue) this.minValue = value;
        if (this.maxValue === null || value > this.maxValue) this.maxValue = value;

        // Update UI
        this.updateDisplay();
        this.drawChart();
        this.setStatus('active');
    }

    updateDisplay() {
        const readingValue = this.element.querySelector('.reading-value');
        const avg = this.getAverageValue();

        if (readingValue) {
            readingValue.textContent = this.value.toFixed(2);
        }

        // Update stats
        const stats = this.element.querySelectorAll('.stat-value');
        if (stats.length >= 3) {
            stats[0].textContent = this.minValue?.toFixed(2) || '--';
            stats[1].textContent = this.maxValue?.toFixed(2) || '--';
            stats[2].textContent = avg.toFixed(2);
        }
    }

    setupChart() {
        if (!this.canvas) return;
        const ctx = this.canvas.getContext('2d');
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    drawChart() {
        if (!this.canvas || !this.history.length) return;

        const ctx = this.canvas.getContext('2d');
        const width = this.canvas.width;
        const height = this.canvas.height;
        const padding = 5;

        // Clear canvas
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, 0, width, height);

        // Find min/max for scaling
        const values = this.history.map(h => h.value);
        const minVal = Math.min(...values);
        const maxVal = Math.max(...values);
        const range = maxVal - minVal || 1;

        // Draw line chart
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 2;
        ctx.beginPath();

        for (let i = 0; i < this.history.length; i++) {
            const x = width - (i / (this.history.length - 1 || 1)) * (width - 2 * padding);
            const y = height - padding - ((this.history[i].value - minVal) / range) * (height - 2 * padding);

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }

        ctx.stroke();

        // Draw current point
        ctx.fillStyle = '#00ff00';
        ctx.beginPath();
        ctx.arc(width - padding, height - padding - ((this.value - minVal) / range) * (height - 2 * padding), 3, 0, Math.PI * 2);
        ctx.fill();
    }

    getAverageValue() {
        if (this.history.length === 0) return 0;
        const sum = this.history.reduce((acc, h) => acc + h.value, 0);
        return sum / this.history.length;
    }

    getUnitForType(sensorType) {
        const units = {
            distance: 'cm',
            temperature: '°C',
            humidity: '%',
            pressure: 'hPa',
            light: 'lux',
            sound: 'dB',
            acceleration: 'm/s²',
            gyro: 'deg/s',
            magnetic: 'mT'
        };
        return units[sensorType] || sensorType;
    }

    formatName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// Export for use in browser
window.SensorPanel = SensorPanel;
