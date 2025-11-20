from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'email', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'first_name', 'last_name', 'email')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if phone_number and password:
            user = authenticate(username=str(phone_number), password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "phone_number" and "password".')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            # User relation
            'user',
            # Шаг 1: Базовая информация
            'full_name',
            'has_self_employment',
            'ready_for_self_employment',
            'main_blog_link',
            'social_links',
            'country',
            'city',
            'age',
            'gender',
            'coverage_regions',
            # Шаг 2: Контент и платформа
            'platforms',
            'blog_topics',
            'blog_description',
            'blog_experience',
            'publication_frequency',
            # Шаг 3: Аудитория
            'subscribers_by_platform',
            'average_reach',
            'audience_gender_age',
            'audience_region',
            'engagement_level',
            # Шаг 4: Опыт и сотрудничество
            'has_collaborations',
            'collaboration_examples',
            'ready_to_share_results',
            'ready_for_paid_ads',
            # Шаг 5: Формат сотрудничества
            'collaboration_formats',
            'ad_pricing',
            'ready_for_barter',
            'barter_categories',
            # Шаг 6: Дополнительно
            'ready_for_brand_projects',
            'products_wont_advertise',
            'blog_management',
            'has_media_kit',
            'media_kit_link',
            'ready_for_blogger_community',
            'additional_info',
            'consent_privacy',
            'consent_marketing_email',
            'consent_marketing_calls',
            # Старые поля (для обратной совместимости)
            'contact',
            'date_of_birth',
            'pickup_point',
            # Статусы
            'is_completed',
            'is_participating',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'is_participating', 'is_completed')

    def validate(self, attrs):
        # Конвертируем пустые строки в None для опциональных полей
        optional_string_fields = [
            'ready_for_self_employment', 'main_blog_link', 'country', 'city',
            'gender', 'coverage_regions', 'blog_description', 'blog_experience',
            'publication_frequency', 'audience_gender_age', 'audience_region',
            'engagement_level', 'ready_to_share_results', 'ready_for_paid_ads',
            'ready_for_barter', 'ready_for_brand_projects', 'products_wont_advertise',
            'blog_management', 'media_kit_link', 'ready_for_blogger_community',
            'additional_info', 'contact', 'pickup_point'
        ]
        
        for field in optional_string_fields:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        # Конвертируем пустые массивы в пустые списки
        array_fields = [
            'social_links', 'platforms', 'blog_topics', 'subscribers_by_platform',
            'average_reach', 'collaboration_examples', 'collaboration_formats',
            'ad_pricing', 'barter_categories'
        ]
        
        for field in array_fields:
            if field in attrs and not isinstance(attrs[field], list):
                attrs[field] = []
        
        return attrs

    def update(self, instance, validated_data):
        try:
            instance = super().update(instance, validated_data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error updating profile instance: {str(e)}')
            raise

        # Проверка обязательных полей (помеченных * в форме)
        try:
            required_fields = [
                # Шаг 1
                bool(instance.full_name and instance.full_name.strip()),
                instance.has_self_employment is not None,
                bool(instance.ready_for_self_employment and instance.ready_for_self_employment.strip()),
                bool(instance.main_blog_link and instance.main_blog_link.strip()),
                bool(instance.social_links and isinstance(instance.social_links, list) and len(instance.social_links) > 0),
                bool(instance.country and instance.country.strip()),
                bool(instance.city and instance.city.strip()),
                instance.age is not None,
                bool(instance.gender and instance.gender.strip()),
                bool(instance.coverage_regions and instance.coverage_regions.strip()),
                # Шаг 2
                bool(instance.platforms and isinstance(instance.platforms, list) and len(instance.platforms) > 0),
                bool(instance.blog_topics and isinstance(instance.blog_topics, list) and len(instance.blog_topics) > 0),
                bool(instance.blog_description and instance.blog_description.strip()),
                bool(instance.blog_experience and instance.blog_experience.strip()),
                bool(instance.publication_frequency and instance.publication_frequency.strip()),
                # Шаг 3
                bool(instance.subscribers_by_platform and isinstance(instance.subscribers_by_platform, list) and len(instance.subscribers_by_platform) > 0),
                bool(instance.average_reach and isinstance(instance.average_reach, list) and len(instance.average_reach) > 0),
                bool(instance.engagement_level and instance.engagement_level.strip()),
                # Шаг 4
                bool(instance.ready_to_share_results and instance.ready_to_share_results.strip()),
                bool(instance.ready_for_paid_ads and instance.ready_for_paid_ads.strip()),
                # Шаг 5
                bool(instance.collaboration_formats and isinstance(instance.collaboration_formats, list) and len(instance.collaboration_formats) > 0),
                bool(instance.ad_pricing and isinstance(instance.ad_pricing, list) and len(instance.ad_pricing) > 0),
                bool(instance.ready_for_barter and instance.ready_for_barter.strip()),
                bool(instance.barter_categories and isinstance(instance.barter_categories, list) and len(instance.barter_categories) > 0),
                # Шаг 6
                bool(instance.ready_for_brand_projects and instance.ready_for_brand_projects.strip()),
                bool(instance.blog_management and instance.blog_management.strip()),
                # has_media_kit теперь опциональное поле (может быть NULL)
                bool(instance.ready_for_blogger_community and instance.ready_for_blogger_community.strip()),
                instance.consent_privacy,
            ]

            # Если has_media_kit = True, то media_kit_link обязателен
            if instance.has_media_kit is True and not (instance.media_kit_link and instance.media_kit_link.strip()):
                required_fields.append(False)

            is_completed = all(required_fields)
            if instance.is_completed != is_completed:
                instance.is_completed = is_completed
                instance.save(update_fields=('is_completed', 'updated_at'))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error checking required fields: {str(e)}')
            # Не прерываем сохранение, если ошибка в проверке обязательных полей

        return instance


class ParticipationSerializer(serializers.Serializer):
    is_participating = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.is_participating = validated_data['is_participating']
        instance.save(update_fields=('is_participating', 'updated_at'))
        return instance

