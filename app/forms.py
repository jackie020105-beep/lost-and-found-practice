"""분실물 등록 필드와 서버 측 입력 검증."""

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

CATEGORIES = ("전자기기", "지갑·카드", "의류·잡화", "도서·문구", "기타")


def strip_text(value):
    return value.strip() if isinstance(value, str) else value


def required_text():
    return [
        DataRequired(message="필수 입력 항목입니다."),
        Length(max=100, message="100자 이내로 입력해 주세요."),
    ]


class ItemForm(FlaskForm):
    title = StringField("물품명", validators=required_text(), filters=[strip_text])
    category = SelectField(
        "분류", choices=[(category, category) for category in CATEGORIES],
        validators=[DataRequired(message="분류를 선택해 주세요.")],
        default="기타",
    )
    found_location = StringField(
        "습득 장소", validators=required_text(), filters=[strip_text]
    )
    storage_location = StringField(
        "보관 장소", validators=required_text(), filters=[strip_text]
    )
    found_date = DateField(
        "습득일", default=date.today,
        validators=[DataRequired(message="올바른 습득일을 입력해 주세요.")],
    )
    description = TextAreaField(
        "물품 설명", filters=[strip_text],
        validators=[Optional(), Length(max=2000, message="설명은 2,000자 이내로 입력해 주세요.")],
    )
    submit = SubmitField("분실물 등록")

    def validate_found_date(self, field):
        if field.data > date.today():
            raise ValidationError("습득일은 오늘 또는 이전 날짜여야 합니다.")
