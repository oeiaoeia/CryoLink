"""
Temperature Simulator Utility
Simulates temperature excursions and thermal buffer calculations
"""
from datetime import datetime, timedelta
import random
import math


class TemperatureSimulator:
    """Simulate temperature behavior for cold-chain shipments"""
    
    def __init__(self, temp_min, temp_max, ambient_temp=25):
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.ambient_temp = ambient_temp
        self.optimal_temp = (temp_min + temp_max) / 2
    
    def simulate_journey(self, duration_hours, num_readings=None):
        """
        Simulate temperature readings for a journey
        """
        if num_readings is None:
            num_readings = int(duration_hours * 2)  # 2 readings per hour
        
        readings = []
        current_temp = self.optimal_temp
        
        for i in range(num_readings):
            # Time progression
            time_offset = (duration_hours / num_readings) * i
            timestamp = datetime.utcnow() - timedelta(hours=duration_hours) + timedelta(hours=time_offset)
            
            # Normal temperature variation
            variation = random.gauss(0, 0.5)
            
            # Simulate loading/unloading events (temperature spikes)
            if i < num_readings * 0.05 or i > num_readings * 0.95:
                # Loading/unloading phase - closer to ambient
                drift = (self.ambient_temp - current_temp) * 0.1
                current_temp += drift + variation
            else:
                # In transit - maintain optimal
                drift = (self.optimal_temp - current_temp) * 0.05
                current_temp += drift + variation
            
            # Occasional equipment fluctuations
            if random.random() < 0.02:  # 2% chance
                current_temp += random.uniform(-2, 2)
            
            readings.append({
                'timestamp': timestamp,
                'temperature': round(current_temp, 1),
                'is_within_range': self.temp_min <= current_temp <= self.temp_max
            })
        
        return readings
    
    def simulate_excursion(self, duration_minutes, starting_temp=None):
        """
        Simulate a temperature excursion event
        Returns excursion data including impact assessment
        """
        if starting_temp is None:
            starting_temp = self.optimal_temp
        
        # Calculate temperature drift toward ambient
        drift_rate = (self.ambient_temp - starting_temp) / 60  # per minute
        
        excursion_readings = []
        current_temp = starting_temp
        
        for minute in range(duration_minutes):
            current_temp += drift_rate * random.uniform(0.8, 1.2)
            excursion_readings.append({
                'minute': minute,
                'temperature': round(current_temp, 1)
            })
        
        final_temp = excursion_readings[-1]['temperature']
        max_temp = max(r['temperature'] for r in excursion_readings)
        
        # Assess impact
        thermal_buffer = self._calculate_thermal_buffer()
        time_in_range = self._time_until_breach(starting_temp)
        
        impact = self._assess_impact(duration_minutes, max_temp, thermal_buffer)
        
        return {
            'starting_temp': starting_temp,
            'final_temp': final_temp,
            'max_temp': max_temp,
            'duration_minutes': duration_minutes,
            'readings': excursion_readings,
            'thermal_buffer_minutes': thermal_buffer,
            'time_until_breach_minutes': time_in_range,
            'impact': impact,
            'product_compromised': duration_minutes > thermal_buffer
        }
    
    def _calculate_thermal_buffer(self):
        """
        Calculate thermal buffer time based on product type
        """
        # Ultra-cold products have shorter buffer
        if self.temp_max <= -60:
            base_buffer = 15
        elif self.temp_max <= -15:
            base_buffer = 30
        else:
            base_buffer = 45
        
        # Add some variation
        return base_buffer + random.randint(-5, 10)
    
    def _time_until_breach(self, starting_temp):
        """
        Calculate time until temperature breaches acceptable range
        """
        if starting_temp < self.temp_min:
            breach_temp = self.temp_min
        else:
            breach_temp = self.temp_max
        
        # Newton's law of cooling approximation
        temp_diff = abs(self.ambient_temp - starting_temp)
        breach_diff = abs(self.ambient_temp - breach_temp)
        
        if temp_diff == 0:
            return 0
        
        # Time constant approximation
        time_constant = 30  # minutes
        time_to_breach = time_constant * math.log(temp_diff / breach_diff)
        
        return max(0, int(time_to_breach))
    
    def _assess_impact(self, duration_minutes, max_temp, thermal_buffer):
        """
        Assess product impact based on excursion parameters
        """
        if duration_minutes <= thermal_buffer * 0.5:
            return {
                'severity': 'low',
                'product_impact': 'none',
                'potency_loss_percent': 0,
                'action': 'Continue monitoring'
            }
        elif duration_minutes <= thermal_buffer:
            return {
                'severity': 'moderate',
                'product_impact': 'minimal',
                'potency_loss_percent': round(random.uniform(0.5, 2), 1),
                'action': 'Monitor closely, document excursion'
            }
        elif duration_minutes <= thermal_buffer * 1.5:
            return {
                'severity': 'high',
                'product_impact': 'moderate',
                'potency_loss_percent': round(random.uniform(2, 10), 1),
                'action': 'Quality assessment required before release'
            }
        else:
            return {
                'severity': 'critical',
                'product_impact': 'compromised',
                'potency_loss_percent': round(random.uniform(10, 50), 1),
                'action': 'Quarantine product, initiate investigation'
            }
    
    def what_if_scenarios(self, current_temp, duration_minutes):
        """
        Generate what-if scenarios for decision support
        """
        scenarios = []
        
        # Scenario 1: Current trajectory
        scenario_1 = self.simulate_excursion(duration_minutes, current_temp)
        scenarios.append({
            'name': 'Current Trajectory',
            'description': f'If temperature remains at {current_temp}°C for {duration_minutes} minutes',
            'result': scenario_1
        })
        
        # Scenario 2: Improved cooling
        improved_temp = (self.temp_min + self.temp_max) / 2
        scenario_2 = self.simulate_excursion(duration_minutes, improved_temp)
        scenarios.append({
            'name': 'Improved Cooling',
            'description': f'If temperature is restored to {improved_temp}°C',
            'result': scenario_2
        })
        
        # Scenario 3: Extended exposure
        extended_duration = duration_minutes * 2
        scenario_3 = self.simulate_excursion(extended_duration, current_temp)
        scenarios.append({
            'name': 'Extended Exposure',
            'description': f'If exposure continues for {extended_duration} minutes',
            'result': scenario_3
        })
        
        return scenarios


class ExcursionPredictor:
    """Predict potential temperature excursions"""
    
    @staticmethod
    def predict_excursion_risk(shipment, route_data, weather_data):
        """
        Predict likelihood of temperature excursion
        """
        risk_factors = []
        
        # Check weather conditions
        if weather_data.get('extreme_heat', False) and shipment.temp_max < 10:
            risk_factors.append({
                'factor': 'Extreme heat at destination',
                'risk_increase': 20
            })
        
        if weather_data.get('extreme_cold', False) and shipment.temp_min > 0:
            risk_factors.append({
                'factor': 'Extreme cold at destination',
                'risk_increase': 15
            })
        
        # Check route characteristics
        if route_data.get('multiple_transfers', False):
            risk_factors.append({
                'factor': 'Multiple handling points',
                'risk_increase': 15
            })
        
        if route_data.get('long_customs_wait', False):
            risk_factors.append({
                'factor': 'Extended customs hold expected',
                'risk_increase': 25
            })
        
        # Check equipment age
        if route_data.get('old_equipment', False):
            risk_factors.append({
                'factor': 'Aging cold-chain equipment',
                'risk_increase': 10
            })
        
        # Calculate total risk
        base_risk = 10  # Base excursion risk
        total_risk = base_risk + sum(f['risk_increase'] for f in risk_factors)
        
        return {
            'excursion_probability': min(100, total_risk),
            'risk_factors': risk_factors,
            'recommendations': ExcursionPredictor._generate_recommendations(risk_factors)
        }
    
    @staticmethod
    def _generate_recommendations(risk_factors):
        """Generate mitigation recommendations"""
        recommendations = []
        
        for factor in risk_factors:
            if 'heat' in factor['factor'].lower():
                recommendations.append('Pre-cool packaging and use enhanced insulation')
            elif 'cold' in factor['factor'].lower():
                recommendations.append('Use heated containers or thermal blankets')
            elif 'transfer' in factor['factor'].lower():
                recommendations.append('Minimize exposure time during transfers')
            elif 'customs' in factor['factor'].lower():
                recommendations.append('Pre-file customs documentation to reduce wait time')
            elif 'equipment' in factor['factor'].lower():
                recommendations.append('Request equipment inspection before loading')
        
        return recommendations
