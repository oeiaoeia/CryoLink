"""
Risk Calculator Utility
Calculates risk scores for shipments based on multiple factors
"""
from datetime import datetime, timedelta
import math


class RiskCalculator:
    """Calculate risk scores for cold-chain shipments"""
    
    # Factor weights
    WEIGHTS = {
        'weather': 0.25,
        'customs': 0.25,
        'carrier': 0.25,
        'temperature': 0.25
    }
    
    @staticmethod
    def calculate_weather_risk(route_data):
        """
        Calculate weather-related risk (0-25 points)
        Higher score = higher risk
        """
        risk = 0
        
        # Check for severe weather conditions
        if route_data.get('has_severe_weather', False):
            risk += 10
        
        # Check for monsoon/storm season
        if route_data.get('is_storm_season', False):
            risk += 8
        
        # Check temperature extremes along route
        if route_data.get('extreme_temps', False):
            risk += 5
        
        # Check for natural disaster risks
        if route_data.get('disaster_risk', False):
            risk += 7
        
        return min(25, risk)
    
    @staticmethod
    def calculate_customs_risk(route_data):
        """
        Calculate customs/congestion risk (0-25 points)
        """
        risk = 0
        
        # Number of border crossings
        border_crossings = route_data.get('border_crossings', 0)
        risk += min(10, border_crossings * 3)
        
        # Historical delay at checkpoints
        avg_delay_hours = route_data.get('avg_customs_delay_hours', 0)
        if avg_delay_hours > 4:
            risk += 10
        elif avg_delay_hours > 2:
            risk += 6
        elif avg_delay_hours > 1:
            risk += 3
        
        # Holiday season congestion
        if route_data.get('is_holiday_season', False):
            risk += 5
        
        return min(25, risk)
    
    @staticmethod
    def calculate_carrier_risk(carrier_data):
        """
        Calculate carrier reliability risk (0-25 points)
        Lower score = better carrier
        """
        risk = 0
        
        # On-time performance
        on_time_rate = carrier_data.get('on_time_rate', 100)
        if on_time_rate < 80:
            risk += 15
        elif on_time_rate < 90:
            risk += 10
        elif on_time_rate < 95:
            risk += 5
        
        # Temperature compliance history
        temp_compliance = carrier_data.get('temp_compliance_rate', 100)
        if temp_compliance < 90:
            risk += 10
        elif temp_compliance < 95:
            risk += 5
        
        # Years in operation
        years_operating = carrier_data.get('years_operating', 0)
        if years_operating < 2:
            risk += 5
        
        return min(25, risk)
    
    @staticmethod
    def calculate_temperature_risk(shipment_data):
        """
        Calculate temperature stability risk (0-25 points)
        """
        risk = 0
        
        # Temperature zone sensitivity
        temp_zone = shipment_data.get('temp_zone', 'refrigerated')
        if temp_zone == 'ultra_cold':
            risk += 10  # Most sensitive
        elif temp_zone == 'frozen':
            risk += 6
        else:
            risk += 3  # Refrigerated
        
        # Thermal buffer time
        buffer_minutes = shipment_data.get('thermal_buffer_minutes', 30)
        if buffer_minutes < 15:
            risk += 10
        elif buffer_minutes < 30:
            risk += 5
        
        # Journey duration vs buffer
        journey_hours = shipment_data.get('journey_hours', 0)
        buffer_hours = buffer_minutes / 60
        if journey_hours > buffer_hours * 10:
            risk += 5
        
        # Previous excursions on this route
        route_excursions = shipment_data.get('route_excursions', 0)
        risk += min(5, route_excursions * 2)
        
        return min(25, risk)
    
    @classmethod
    def calculate_total_risk(cls, route_data, carrier_data, shipment_data):
        """
        Calculate total risk score (0-100)
        """
        weather_risk = cls.calculate_weather_risk(route_data)
        customs_risk = cls.calculate_customs_risk(route_data)
        carrier_risk = cls.calculate_carrier_risk(carrier_data)
        temp_risk = cls.calculate_temperature_risk(shipment_data)
        
        # Apply weights
        total = (
            weather_risk * cls.WEIGHTS['weather'] / 0.25 +
            customs_risk * cls.WEIGHTS['customs'] / 0.25 +
            carrier_risk * cls.WEIGHTS['carrier'] / 0.25 +
            temp_risk * cls.WEIGHTS['temperature'] / 0.25
        ) / 4
        
        return round(min(100, max(0, total)), 1)
    
    @staticmethod
    def get_risk_level(score):
        """Get risk level label based on score"""
        if score <= 30:
            return 'low'
        elif score <= 60:
            return 'moderate'
        else:
            return 'high'
    
    @staticmethod
    def get_risk_color(score):
        """Get color code for risk level"""
        if score <= 30:
            return '#00C853'  # Green
        elif score <= 60:
            return '#FFB300'  # Amber
        else:
            return '#D32F2F'  # Red


class IntegrityCalculator:
    """Calculate cold-chain integrity scores"""
    
    @staticmethod
    def calculate_integrity(shipment, temperature_logs, excursions):
        """
        Calculate integrity score (0-100) based on:
        - Temperature stability
        - Handling events
        - Transit time performance
        - Excursion history
        """
        score = 100
        
        # Temperature stability (max -40 points)
        if temperature_logs:
            compliant = sum(1 for log in temperature_logs if log.is_within_range)
            compliance_rate = compliant / len(temperature_logs)
            if compliance_rate < 1:
                score -= (1 - compliance_rate) * 40
        
        # Excursions (max -30 points)
        for excursion in excursions:
            if excursion.severity == 'critical':
                score -= 15
            elif excursion.severity == 'high':
                score -= 10
            elif excursion.severity == 'moderate':
                score -= 5
            else:
                score -= 2
        
        # Transit time performance (max -20 points)
        if shipment.estimated_arrival and shipment.actual_arrival:
            delay = shipment.actual_arrival - shipment.estimated_arrival
            delay_hours = delay.total_seconds() / 3600
            if delay_hours > 0:
                score -= min(20, delay_hours * 2)
        
        # Handling events (max -10 points)
        # (Would count rough handling events from IoT sensors)
        
        return round(max(0, min(100, score)), 1)
