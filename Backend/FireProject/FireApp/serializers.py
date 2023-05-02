from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class BaseSerializer(serializers.Serializer):
    subject_tag = serializers.CharField(max_length=10)
    date_time = serializers.DateTimeField('%Y-%m-%dT%H:%M:%S')

    def is_valid(self, *, raise_exception=False):
        # This implementation is the same as the default,
        # except that we use lists, rather than dicts, as the empty case.
        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = []
                self._errors = exc.detail
            else:
                self._errors = []

        if self._errors and raise_exception:
            # print(self.errors)
            # print(self._errors)

            # print(self.errors.get('email') == '19')
            # print(self.errors.get('email')[0])
            if self.errors.get('email') and self.errors.get('email')[0] == '19':
                raise ValidationError({'fields_error': '19'}) #self.errors})
            else:
                raise ValidationError({'fields_error': '18'}) # self.errors})

        return not bool(self._errors)


class ShapeSerializer(BaseSerializer):
    pass


class PDFSerializer(BaseSerializer):
    operator_fio = serializers.CharField(max_length=100)
    cloud_shielding = serializers.IntegerField()