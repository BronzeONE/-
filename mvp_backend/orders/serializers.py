from rest_framework import serializers

from .models import CreatingOrder, Purchase, TestReport


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
    has_report = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = (
            'id',
            'external_id',
            'article',
            'pickup_point',
            'status',
            'metadata',
            'has_report',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields
    
    def get_has_report(self, obj):
        return hasattr(obj, 'test_report')


class OrderDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=('approve', 'reject'))
    purchase_metadata = serializers.JSONField(required=False)
    external_id = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    pickup_point = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        action = attrs['action']
        if action == 'approve':
            attrs.setdefault('purchase_metadata', {})
        return attrs


class TestReportSerializer(serializers.ModelSerializer):
    purchase_id = serializers.IntegerField(source='purchase.id', read_only=True)
    purchase_article = serializers.CharField(source='purchase.article', read_only=True)
    
    class Meta:
        model = TestReport
        fields = (
            'id',
            'purchase_id',
            'purchase_article',
            'full_name',
            'contact',
            'item_name',
            'category',
            'received_at',
            'completed_at',
            'report_type',
            'proof_links',
            'proof_files',
            'score_overall',
            'score_expectation_fit',
            'score_quality_effect',
            'score_usability',
            'score_value_for_money',
            'score_recommend',
            'likes',
            'improvements',
            'review_text',
            'emotions_3_words',
            'issues_occured',
            'issues_note',
            'would_buy',
            'ready_for_next',
            'consent_truthful',
            'consent_use_materials',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_score_overall(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('Оценка должна быть от 1 до 5')
        return value
    
    def validate_score_expectation_fit(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('Оценка должна быть от 1 до 5')
        return value
    
    def validate_score_quality_effect(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('Оценка должна быть от 1 до 5')
        return value
    
    def validate_score_usability(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('Оценка должна быть от 1 до 5')
        return value
    
    def validate_score_value_for_money(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('Оценка должна быть от 1 до 5')
        return value
    
    def validate_score_recommend(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError('Оценка должна быть от 0 до 10')
        return value
    
    def validate_review_text(self, value):
        if value and len(value) > 1000:
            raise serializers.ValidationError('Текст отзыва не должен превышать 1000 символов')
        return value
    
    def validate_proof_files(self, value):
        if isinstance(value, list) and len(value) > 5:
            raise serializers.ValidationError('Можно загрузить не более 5 файлов')
        return value

