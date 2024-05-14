from rest_framework import serializers
from .models import OccupancyMetrics
from parking_lot.models import ParkingLot
import datetime

class OccupancyAdjustmentSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    adjustment = serializers.IntegerField()  # +1 or -1

    def update_occupancy_metrics(self, address, adjustment):
        parking_lot = ParkingLot.objects.get(street_address=address)
        metrics, created = OccupancyMetrics.objects.get_or_create(parking_lot=parking_lot)
        now = datetime.datetime.now()

        # Use strftime to get the weekday and hour
        weekday = now.strftime('%A')
        current_hour = now.strftime('%H:00')  # Format the hour as HH:00

        # Reset weekly data if it's a new week
        if now.date() > metrics.last_update:
            if (now - datetime.datetime.combine(metrics.last_update, datetime.time.min)).days >= 7:
                # Update average occupancy
                if current_hour not in metrics.average_occupancy[weekday]:
                    metrics.average_occupancy[weekday][current_hour] = adjustment
                else:
                    count_hours = metrics.average_occupancy[weekday].get(current_hour, 0) + 1
                    current_avg = metrics.average_occupancy[weekday][current_hour]
                    new_avg = ((current_avg * count_hours) + adjustment) / (count_hours + 1)
                    metrics.average_occupancy[weekday][current_hour] = new_avg
                    metrics.average_occupancy[weekday][current_hour] = count_hours + 1
                metrics.current_occupancy = default_week_structure()  # Resetting to default structure

        # Update current occupancy
        if current_hour not in metrics.current_occupancy[weekday]:
            metrics.current_occupancy[weekday][current_hour] = 0
        metrics.current_occupancy[weekday][current_hour] += adjustment

        # Adjust total current occupancy
        metrics.total_current_occupancy = max(0, metrics.total_current_occupancy + adjustment)

        # Save the metrics and update the last update date
        metrics.last_update = now.date()
        metrics.save()
        return metrics


class OccupancyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupancyMetrics
        fields = ['current_occupancy', 'average_occupancy']


class AddressSerializer(serializers.Serializer):
    street_address = serializers.CharField(max_length=255)
