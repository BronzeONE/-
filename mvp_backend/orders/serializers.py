from rest_framework import serializers

from .models import CreatingOrder, Purchase


class CreatingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatingOrder
        fields = (
            'id',
            'article',
            'title',
            'pickup_point',
            'notes',
            'status',
            'payload',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = (
            'id',
            'external_id',
            'article',
            'pickup_point',
            'status',
            'metadata',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class OrderDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=('approve', 'reject'))
    purchase_metadata = serializers.JSONField(required=False)
    external_id = serializers.CharField(max_length=255, required=False)
    pickup_point = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        action = attrs['action']
        if action == 'approve':
            attrs.setdefault('purchase_metadata', {})
        return attrs

