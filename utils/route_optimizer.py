"""
Route Optimizer Utility
Finds and compares optimal routes for cold-chain shipments
"""
from datetime import datetime, timedelta
from .risk_calculator import RiskCalculator


class RouteOptimizer:
    """Find and compare optimal shipping routes"""
    
    # Transport mode characteristics
    TRANSPORT_MODES = {
        'air': {
            'speed_multiplier': 1.0,
            'cost_multiplier': 3.0,
            'co2_per_km': 0.5,
            'temp_risk_base': 15,
            'handling_events': 4
        },
        'sea': {
            'speed_multiplier': 0.2,
            'cost_multiplier': 0.5,
            'co2_per_km': 0.04,
            'temp_risk_base': 10,
            'handling_events': 2
        },
        'road': {
            'speed_multiplier': 0.4,
            'cost_multiplier': 1.0,
            'co2_per_km': 0.1,
            'temp_risk_base': 12,
            'handling_events': 3
        },
        'rail': {
            'speed_multiplier': 0.35,
            'cost_multiplier': 0.7,
            'co2_per_km': 0.05,
            'temp_risk_base': 11,
            'handling_events': 2
        }
    }
    
    def __init__(self):
        self.risk_calculator = RiskCalculator()
    
    def generate_route_options(self, origin, destination, shipment_requirements):
        """
        Generate multiple route options for comparison
        """
        options = []
        
        # Air Express Route
        air_route = self._create_air_express_route(origin, destination, shipment_requirements)
        options.append(air_route)
        
        # Sea Freight Route
        sea_route = self._create_sea_freight_route(origin, destination, shipment_requirements)
        options.append(sea_route)
        
        # Hybrid Route (Air + Road)
        hybrid_route = self._create_hybrid_route(origin, destination, shipment_requirements)
        options.append(hybrid_route)
        
        # Sort by overall score
        options.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return options
    
    def _create_air_express_route(self, origin, destination, requirements):
        """Create air express route option"""
        distance_km = self._estimate_distance(origin, destination)
        base_duration = distance_km / 800  # Average air speed
        
        # Add handling time
        total_duration = base_duration + 6  # 6 hours for handling
        
        # Calculate metrics
        cost = distance_km * 0.5 * self.TRANSPORT_MODES['air']['cost_multiplier']
        co2 = distance_km * self.TRANSPORT_MODES['air']['co2_per_km']
        
        # Risk calculation
        route_data = {
            'border_crossings': 2,
            'avg_customs_delay_hours': 2,
            'is_holiday_season': False,
            'has_severe_weather': False,
            'is_storm_season': False,
            'extreme_temps': False,
            'disaster_risk': False
        }
        
        carrier_data = {
            'on_time_rate': 95,
            'temp_compliance_rate': 98,
            'years_operating': 10
        }
        
        shipment_data = {
            'temp_zone': requirements.get('temp_zone', 'refrigerated'),
            'thermal_buffer_minutes': requirements.get('thermal_buffer', 30),
            'journey_hours': total_duration,
            'route_excursions': 0
        }
        
        risk_score = self.risk_calculator.calculate_total_risk(
            route_data, carrier_data, shipment_data
        )
        
        return {
            'route_type': 'air_express',
            'name': 'Air Express',
            'icon': '✈️',
            'transport_modes': ['air'],
            'total_distance_km': distance_km,
            'total_duration_hours': total_duration,
            'estimated_cost': cost,
            'co2_emissions_kg': co2,
            'risk_score': risk_score,
            'recommended': True,
            'legs': self._generate_air_legs(origin, destination, total_duration)
        }
    
    def _create_sea_freight_route(self, origin, destination, requirements):
        """Create sea freight route option"""
        distance_km = self._estimate_distance(origin, destination) * 1.3  # Sea routes longer
        base_duration = distance_km / 30  # Average ship speed
        
        # Add port handling time
        total_duration = base_duration + 48  # 2 days for port handling
        
        # Calculate metrics
        cost = distance_km * 0.1 * self.TRANSPORT_MODES['sea']['cost_multiplier']
        co2 = distance_km * self.TRANSPORT_MODES['sea']['co2_per_km']
        
        route_data = {
            'border_crossings': 1,
            'avg_customs_delay_hours': 4,
            'is_holiday_season': False,
            'has_severe_weather': False,
            'is_storm_season': False,
            'extreme_temps': False,
            'disaster_risk': False
        }
        
        carrier_data = {
            'on_time_rate': 88,
            'temp_compliance_rate': 95,
            'years_operating': 15
        }
        
        shipment_data = {
            'temp_zone': requirements.get('temp_zone', 'refrigerated'),
            'thermal_buffer_minutes': requirements.get('thermal_buffer', 30),
            'journey_hours': total_duration,
            'route_excursions': 0
        }
        
        risk_score = self.risk_calculator.calculate_total_risk(
            route_data, carrier_data, shipment_data
        )
        
        return {
            'route_type': 'sea_freight',
            'name': 'Sea Freight',
            'icon': '🚢',
            'transport_modes': ['sea'],
            'total_distance_km': distance_km,
            'total_duration_hours': total_duration,
            'estimated_cost': cost,
            'co2_emissions_kg': co2,
            'risk_score': max(0, risk_score - 10),  # Sea is generally more stable
            'recommended': False,
            'greenest': True,
            'legs': self._generate_sea_legs(origin, destination, total_duration)
        }
    
    def _create_hybrid_route(self, origin, destination, requirements):
        """Create hybrid air + road route option"""
        distance_km = self._estimate_distance(origin, destination)
        air_distance = distance_km * 0.7
        road_distance = distance_km * 0.3
        
        base_duration = (air_distance / 800) + (road_distance / 80)
        
        # Add handling time
        total_duration = base_duration + 10
        
        # Calculate metrics
        cost = (air_distance * 0.5 + road_distance * 0.3) * 0.8  # 20% discount for hybrid
        co2 = (air_distance * 0.5 * 0.7 + road_distance * 0.1 * 0.3)
        
        route_data = {
            'border_crossings': 3,
            'avg_customs_delay_hours': 2.5,
            'is_holiday_season': False,
            'has_severe_weather': False,
            'is_storm_season': False,
            'extreme_temps': False,
            'disaster_risk': False
        }
        
        carrier_data = {
            'on_time_rate': 92,
            'temp_compliance_rate': 96,
            'years_operating': 8
        }
        
        shipment_data = {
            'temp_zone': requirements.get('temp_zone', 'refrigerated'),
            'thermal_buffer_minutes': requirements.get('thermal_buffer', 30),
            'journey_hours': total_duration,
            'route_excursions': 0
        }
        
        risk_score = self.risk_calculator.calculate_total_risk(
            route_data, carrier_data, shipment_data
        )
        
        return {
            'route_type': 'hybrid',
            'name': 'Hybrid (Air + Road)',
            'icon': '✈️🚛',
            'transport_modes': ['air', 'road'],
            'total_distance_km': distance_km,
            'total_duration_hours': total_duration,
            'estimated_cost': cost,
            'co2_emissions_kg': co2,
            'risk_score': risk_score,
            'recommended': False,
            'best_balance': True,
            'legs': self._generate_hybrid_legs(origin, destination, total_duration)
        }
    
    def _estimate_distance(self, origin, destination):
        """Estimate distance between two points (simplified)"""
        # In production, use actual geocoding
        return 8000  # Default estimate
    
    def _generate_air_legs(self, origin, destination, total_duration):
        """Generate legs for air route"""
        return [
            {'name': 'Origin Pickup', 'mode': 'road', 'duration': 2},
            {'name': f'{origin} Hub', 'mode': 'air', 'duration': total_duration * 0.3},
            {'name': 'Transit Hub', 'mode': 'air', 'duration': total_duration * 0.5},
            {'name': f'{destination} Hub', 'mode': 'air', 'duration': total_duration * 0.15},
            {'name': 'Final Delivery', 'mode': 'road', 'duration': 3}
        ]
    
    def _generate_sea_legs(self, origin, destination, total_duration):
        """Generate legs for sea route"""
        return [
            {'name': 'Origin Pickup', 'mode': 'road', 'duration': 4},
            {'name': f'{origin} Port', 'mode': 'sea', 'duration': total_duration * 0.85},
            {'name': f'{destination} Port', 'mode': 'sea', 'duration': total_duration * 0.1},
            {'name': 'Final Delivery', 'mode': 'road', 'duration': 6}
        ]
    
    def _generate_hybrid_legs(self, origin, destination, total_duration):
        """Generate legs for hybrid route"""
        return [
            {'name': 'Origin Pickup', 'mode': 'road', 'duration': 2},
            {'name': f'{origin} Hub', 'mode': 'air', 'duration': total_duration * 0.4},
            {'name': 'Regional Hub', 'mode': 'air', 'duration': total_duration * 0.35},
            {'name': 'Ground Transport', 'mode': 'road', 'duration': total_duration * 0.2},
            {'name': 'Final Delivery', 'mode': 'road', 'duration': 4}
        ]
    
    def compare_routes(self, options):
        """Compare routes and provide recommendations"""
        comparison = {
            'fastest': min(options, key=lambda x: x['total_duration_hours']),
            'cheapest': min(options, key=lambda x: x['estimated_cost']),
            'greenest': min(options, key=lambda x: x['co2_emissions_kg']),
            'lowest_risk': min(options, key=lambda x: x['risk_score'])
        }
        
        # Add comparison notes
        for option in options:
            notes = []
            if option == comparison['fastest']:
                notes.append('Fastest option')
            if option == comparison['cheapest']:
                notes.append('Most economical')
            if option == comparison['greenest']:
                notes.append('Lowest CO₂ emissions')
            if option == comparison['lowest_risk']:
                notes.append('Lowest risk')
            
            option['notes'] = notes
        
        return comparison
