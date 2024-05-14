from rest_framework import serializers
from .models import IncomeMetrics
from parking_lot.models import ParkingLot
import datetime

class IncomeAdjustmentSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def update_income_metrics(self, address, amount):
        parking_lot = ParkingLot.objects.get(street_address=address)
        metrics, created = IncomeMetrics.objects.get_or_create(parking_lot=parking_lot)
        now = datetime.datetime.now()

        # Get the current weekday and month
        weekday = now.strftime('%A')
        month = now.strftime('%B')
        year = str(now.year)

        # Update daily current and average
        daily_data = metrics.daily_current.get(weekday, 0)
        metrics.daily_current[weekday] = daily_data + float(amount)

        daily_avg_data = metrics.daily_average.get(weekday, 0)
        if created or daily_avg_data == 0:
            metrics.daily_average[weekday] = float(amount)
        else:
            count = metrics.daily_average.get(weekday, 0) + 1
            new_avg = ((daily_avg_data * (count - 1)) + float(amount)) / count
            metrics.daily_average[weekday] = new_avg
            metrics.daily_average[weekday] = count

        # Update monthly total
        monthly_total = metrics.monthly_total.get(month, 0)
        metrics.monthly_total[month] = monthly_total + float(amount)

        # Initialize and update yearly total
        if year not in metrics.yearly_total:
            metrics.yearly_total[year] = 0
        metrics.yearly_total[year] += float(amount)

        # Save updates
        metrics.last_update = now.date()
        metrics.save()
        return metrics


class IncomeMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeMetrics
        fields = ['daily_current', 'daily_average', 'monthly_total', 'yearly_total']


class AddressSerializer(serializers.Serializer):
    street_address = serializers.CharField(max_length=255)
