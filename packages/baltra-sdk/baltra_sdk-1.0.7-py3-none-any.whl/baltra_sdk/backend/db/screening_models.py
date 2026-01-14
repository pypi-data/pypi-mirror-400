# from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Index, CheckConstraint, text, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

db = SQLAlchemy()


def build_db_url_from_settings(settings) -> str:
    """Build database URL from settings object."""
    return (
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


class DBShim:
    """
    Database session manager for lambdas and non-Flask contexts.
    Allows using Flask-SQLAlchemy models with explicit sessions.
    """
    def __init__(self, db_url: str):
        """
        Initialize DBShim with a database URL.
        
        Args:
            db_url: PostgreSQL connection string
        """
        self.engine = create_engine(
            db_url,
            poolclass=NullPool,
            future=True,
        )
        self._SessionFactory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
        self.Session = scoped_session(self._SessionFactory)
        
        # Bind Flask-SQLAlchemy models metadata to this engine
        # This allows using db.Model classes with explicit sessions
        db.Model.metadata.bind = self.engine

    @classmethod
    def from_settings(cls, settings) -> "DBShim":
        """Create DBShim from settings object."""
        return cls(build_db_url_from_settings(settings))

    @property
    def session(self):
        """Get a new database session."""
        return self.Session()

    def remove_session(self):
        """Remove the current session from the scoped session registry."""
        self.Session.remove()

ResponseTypeEnum = db.Enum(
    'text', 'location', 'voice', 'phone_reference', 'interactive', 'name', 'location_critical', 
    name='response_type_enum', 
    create_type=False
)
CompanyScreeningGroupLogicEnum = db.Enum(
    'BUSINESS_UNIT', 
    'ROLES', 
    name='company_screening_group_logic_enum', 
    create_type=False
)
UserPermissionEnum = db.Enum(
    'ENABLE_BILLING_TAB',
    'ENABLE_BUSINESS_UNIT_EDIT_TAB',
    'ENABLE_INTERVIEWED_CANDIDATES_EDIT_TAB',
    name='user_permission_enum',
    create_type=False
)

# TODO
# 1. Create a table to define what we show in the dashboard for each user and company group [DONE]
# 2. Expand CompanyGroups attributes [PENDING]
# 3. Define where we will define which funnel states require a business unit [PENDING]


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    cognito_sub = db.Column(db.String(255), unique=True, nullable=False, index=True)

    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    notify_interviews_email_enabled = db.Column(db.Boolean, nullable=False, default=True)
    notify_pulse_weekly_email_enabled = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    permissions = db.Column(db.ARRAY(UserPermissionEnum), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"), onupdate=db.text("now()"))

    company_group_ids = db.Column(db.JSON, nullable=True) 
    business_unit_ids = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<User {self.id} {self.email}>'


# Company Information Tables
class CompanyGroups(db.Model):
    __tablename__ = "company_groups"

    company_group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.Text)
    wa_id = db.Column(db.String(50))
    phone = db.Column(db.String(50))

    company_screening_group_logic = db.Column(CompanyScreeningGroupLogicEnum)
    
    __table_args__ = (
        db.Index("idx_company_groups_name", "name"),
    )
    

class BusinessUnits(db.Model):
    __tablename__ = "business_units"

    # General Business Unit Information
    business_unit_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.Text)
    description = db.Column(db.Text)
    website = db.Column(db.Text)
    benefits = db.Column(MutableList.as_mutable(db.JSON), default=list)
    general_faq = db.Column(db.JSON)  
    # General FAQ Structure
    # {
    #     "location": {
    #         "Q1":"What is the address of the company?",
    #         "A1": "123 Main St, Anytown, USA"
    #     },
    #     "salary": {
    #         "Q1":"What is the salary of the company?",
    #         "A1": "$100,000"
    #     },
    #     "shift": {
    #         "Q1":"What is the shift of the company?",
    #         "A1": "9:00 AM - 5:00 PM"
    #     },
    #     "custom-1": {}
    # }
    phone = db.Column(db.String)
    hr_contact = db.Column(db.Text)
    additional_info = db.Column(db.Text)

    # Interview Information
    interview_excluded_dates = db.Column(MutableList.as_mutable(db.JSON), default=list)
    interview_days = db.Column(MutableList.as_mutable(db.JSON), default=list)
    interview_hours = db.Column(MutableList.as_mutable(db.JSON), default=list)
    interview_address_json = db.Column(db.JSON)
    max_interviews_per_slot = db.Column(db.Integer, nullable=True)
    

    # Assistant Information
    classifier_assistant_id = db.Column(db.String)
    general_purpose_assistant_id = db.Column(db.String)
    maps_link_json = db.Column(db.JSON)
    ad_trigger_phrase = db.Column(db.Text)
    reminder_schedule = db.Column(db.JSON, nullable=False, default=dict)
    customer_id = db.Column(db.String(50))
    timezone = db.Column(db.String(50), nullable=False, server_default=text("'America/Mexico_City'"), default="America/Mexico_City")
    qr_attendance_s3_path = db.Column(db.String(500), nullable=True)
    referral_options = db.Column(
        db.JSON,
        nullable=True,
        server_default=text("""'["Facebook","Flyer","Manta de la Empresa","Referido","Otra"]'""")
    )
    maximum_location_km = db.Column(db.Float, nullable=True, server_default=db.text("30.0"), default=30.0)
    
    # Meta Business Information
    wa_id = db.Column(db.String)
    company_is_verified_by_meta = db.Column(db.Boolean, nullable=False, server_default=db.text("true"), default=True)

    # Company Group Information
    company_group_id = db.Column(db.Integer, db.ForeignKey("company_groups.company_group_id", ondelete="SET NULL"))

    __table_args__ = (
        CheckConstraint("char_length(description) <= 250", name="description_length_check"),
    )


class ProductUsage(db.Model):
    __tablename__ = "product_usage"
    
    product_usage_id = db.Column(db.Integer, primary_key=True)


class DashboardConfigurations(db.Model):
    __tablename__ = "dashboard_configurations"

    dashboard_configuration_id = db.Column(db.Integer, primary_key=True)
    funnel_states_baltra = db.Column(db.JSON) # ['Evaluados', 'Citados', 'Entrevistados', 'Contratados', 'Ingresados']
    funnel_states_business_unit = db.Column(db.JSON) # ['Pendientes', 'Confirmados', 'No contestaron']

    show_lastest_ad_campaigns = db.Column(db.Boolean, nullable=False, default=True)
    show_hiring_volume = db.Column(db.Boolean, nullable=False, default=True)
    show_phone_interview_information = db.Column(db.Boolean, nullable=False, default=True)
    show_onboarding_tab = db.Column(db.Boolean, nullable=False, default=True)
    show_business_unit_profile_tab = db.Column(db.Boolean, nullable=False, default=True)

    interviewd_candidates_keys = db.Column(db.JSON) # ['Estado', 'Fecha de entrevista', 'Hora de entrevista', 'Dirección de entrevista', 'Mapa de entrevista', ...]
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete="CASCADE"), nullable=False)


class HiringObjectives(db.Model):
    __tablename__ = "hiring_objectives"

    hiring_objective_id = db.Column(db.Integer, primary_key=True)
    company_group_id = db.Column(db.Integer, db.ForeignKey('company_groups.company_group_id', ondelete="CASCADE"), nullable=False) 
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete="CASCADE"), nullable=False)
    objective_type = db.Column(db.Text, nullable=False)
    objective_name = db.Column(db.Text, nullable=False)
    objective_duration = db.Column(db.Date, nullable=False)
    objective_created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))

class Roles(db.Model):
    __tablename__ = 'roles'

    role_id = db.Column(db.Integer, primary_key=True)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete="CASCADE"), nullable=False)
    role_name = db.Column(db.Text, nullable=False)
    role_info = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    set_id = db.Column(db.Integer, db.ForeignKey('question_sets.set_id', ondelete="SET NULL"))
    eligibility_criteria = db.Column(db.JSON)
    default_role = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    shift = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id", ondelete="SET NULL"))
    location_id_interview = db.Column(db.Integer, db.ForeignKey("locations.location_id", ondelete="SET NULL"))

    __table_args__ = (
        CheckConstraint("char_length(role_name) <= 24", name="role_name_length_check"),
        CheckConstraint("char_length(shift) <= 72", name="shift_length_check"), 
    )
    
class Locations(db.Model):
    __tablename__ = 'locations'

    location_id = db.Column(db.Integer, primary_key=True)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete='CASCADE'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    url = db.Column(db.Text)
    address = db.Column(db.Text)

    # Relationships
    business_unit = db.relationship("BusinessUnits", backref="locations")

    # Constraints
    __table_args__ = (
        db.CheckConstraint('latitude BETWEEN -90 AND 90', name='check_valid_latitude'),
        db.CheckConstraint('longitude BETWEEN -180 AND 180', name='check_valid_longitude'),
        db.Index('idx_locations_business_unit', 'business_unit_id'),
    )



# Candidate Information Tables
class Candidates(db.Model):
    __tablename__ = "candidates"

    candidate_id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), nullable=False)
    name = db.Column(db.Text)
    age = db.Column(db.Integer)
    gender = db.Column(db.Text)
    education_level = db.Column(db.Text)
    source = db.Column(db.Text)
    referred_by = db.Column(db.Text, nullable=True, server_default="Baltra", default="Baltra")
    grade = db.Column(db.Integer)
    funnel_state = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))
    start_date = db.Column(db.Date)


    interview_date_time = db.Column(db.DateTime(timezone=True))
    interview_reminder_sent = db.Column(db.Boolean, nullable=False, default=False)
    interview_address = db.Column(db.Text)
    interview_map_link = db.Column(db.Text)
    interview_confirmed = db.Column(db.Boolean, default=None)
    
    travel_time_minutes = db.Column(db.Integer, server_default='0')
    application_reminder_sent = db.Column(db.Boolean, default=False)
    flow_state = db.Column(db.String(50), nullable=False, server_default="respuesta")
    eligible_roles = db.Column(db.JSON)
    reschedule_sent = db.Column(db.Boolean, default=False)
    rejected_reason = db.Column(db.Text)
    screening_rejected_reason = db.Column(db.Text)
    end_flow_rejected = db.Column(db.Boolean, nullable=False, default=False)
    worked_here = db.Column(db.Boolean, nullable=True) 
    eligible_companies = db.Column(db.JSON, nullable=True)
    appointment_reminder_counters = db.Column(db.JSON, nullable=True, default=lambda: {"phone_call_count": 0, "message_count": 0})
    coordinates_json = db.Column(db.JSON, nullable=True)

    # Specific Business Unit Attributes
    especific_business_unit_attributes = db.Column(db.JSON, nullable=True)

    # Relationships
    company_group_id = db.Column(db.Integer, db.ForeignKey("company_groups.company_group_id"), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id", ondelete="SET NULL"))
    business_unit_id = db.Column(db.Integer, db.ForeignKey("business_units.business_unit_id", ondelete="CASCADE"))
    

    __table_args__ = (
        db.PrimaryKeyConstraint('candidate_id', name='candidates_pkey1'),
        db.Index('idx_candidates_company_group_id', 'company_group_id'),
        db.Index('idx_candidates_business_unit_id', 'business_unit_id'),
        db.Index('idx_candidates_company_group_name', 'company_group_id', 'name'),
        db.Index('idx_candidates_capacity_check', 'business_unit_id', 'interview_date_time', 'funnel_state'),  # For capacity checking performance
        # Optional functional index for case-insensitive prefix searches (requires migration support in production)
        # db.Index('idx_candidates_company_lower_name', db.text('company_group_id'), db.text('lower(name)')),
    )

class CandidateFunnelLog(db.Model):
    __tablename__ = 'candidate_funnel_logs'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id', ondelete='CASCADE'), nullable=False)
    previous_funnel_state = db.Column(db.Text)
    new_funnel_state = db.Column(db.Text, nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    # Relationship to Candidate
    candidate = db.relationship("Candidates", backref="funnel_logs")

    __table_args__ = (
        db.Index('candidate_funnel_candidate_id_idx', 'candidate_id'),
        db.Index('candidate_funnel_new_funnel_state_idx', 'new_funnel_state'),
        db.Index('idx_cfl_candidate_changed', 'candidate_id', db.text('changed_at DESC')),
        db.Index('idx_cfl_changed_at', 'changed_at'),
        db.Index('idx_cfl_prev_new_changed', 'previous_funnel_state', 'new_funnel_state', 'changed_at'),
        db.Index('idx_cfl_new_state', 'new_funnel_state'),
    )




# Candidate Interaction Guides Tables
class QuestionSets(db.Model):
    __tablename__ = "question_sets"

    set_id = db.Column(db.Integer, primary_key=True)
    business_unit_id = db.Column(db.Integer, db.ForeignKey("business_units.business_unit_id", ondelete="CASCADE"), nullable=True)
    set_name = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))
    general_set = db.Column(db.Boolean, nullable=False, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey("company_groups.company_group_id", ondelete="CASCADE"),nullable=True)

    business_unit = db.relationship("BusinessUnits", backref="question_sets")
    group = db.relationship("CompanyGroups", backref="question_sets")
    screening_questions = db.relationship("ScreeningQuestions", backref="question_set", cascade="all, delete-orphan")
    __table_args__ = (
        Index(
            'one_general_set_per_business_unit',
            'business_unit_id',
            'group_id',
            unique=True,
            postgresql_where=db.text('general_set IS TRUE')
        ),
        db.CheckConstraint(
            "(business_unit_id IS NOT NULL AND group_id IS NULL) OR "
            "(business_unit_id IS NULL AND group_id IS NOT NULL)",
            name="business_unit_or_group"
        ),
    )

class ScreeningQuestions(db.Model):
    __tablename__ = "screening_questions"

    question_id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey("question_sets.set_id", ondelete="CASCADE"), nullable=False)
    position = db.Column(db.SmallInteger, nullable=False)
    question = db.Column(db.Text, nullable=False)
    response_type = db.Column(ResponseTypeEnum, nullable=False)
    question_metadata = db.Column(db.JSON)
    end_interview_answer = db.Column(db.Text)
    example_answer = db.Column(db.Text)
    is_blocked = db.Column(db.Boolean, default=False)
    eligibility_question = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    screening_answers = db.relationship("ScreeningAnswers", backref="question", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('set_id', 'position', name='screening_questions_set_id_position_key'),
        db.Index('idx_questions_set_pos', 'set_id', 'position')
    )

class ScreeningAnswers(db.Model):
    __tablename__ = "screening_answers"

    answer_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("screening_questions.question_id", ondelete="CASCADE"), nullable=False)
    answer_raw = db.Column(db.Text)
    answer_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))

    __table_args__ = (
        db.UniqueConstraint('candidate_id', 'question_id', name='screening_answers_candidate_id_question_id_key'),
        db.Index('idx_answers_candidate', 'candidate_id'),
        db.Index('idx_answers_question', 'question_id')
    )

class MessageTemplates(db.Model):
    __tablename__ = 'message_templates'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.Text, nullable=False)
    button_trigger = db.Column(db.Text)
    type = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    interactive_type = db.Column(db.Text)
    button_keys = db.Column(db.JSON)
    footer_text = db.Column(db.Text)
    header_type = db.Column(db.Text)
    header_content = db.Column(db.Text)
    parameters = db.Column(db.JSON)
    template = db.Column(db.Text)
    variables = db.Column(db.JSON)
    url_keys = db.Column(db.JSON)
    header_base = db.Column(db.Text)
    flow_keys = db.Column(db.JSON)
    flow_action_data = db.Column(db.JSON)
    document_link = db.Column(db.Text)  # renamed from 'link'
    filename = db.Column(db.Text)
    flow_name = db.Column(db.Text)
    flow_cta = db.Column(db.Text)
    list_options = db.Column(db.JSON)             # [{"id": "opt_1", "title": "Sí", "description": "Confirmar asistencia"}]
    list_section_title = db.Column(db.Text)  
    display_name = db.Column(db.Text)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete="CASCADE"))
    business_unit = db.relationship("BusinessUnits", backref="message_templates")

class PhoneInterviewQuestions(db.Model):
    __tablename__ = 'phone_interview_questions'

    id = db.Column(db.Integer, primary_key=True)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id', ondelete='SET NULL'))
    question_text = db.Column(db.Text, nullable=False)
    position = db.Column(db.SmallInteger, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))

    # Relationships
    business_unit = db.relationship('BusinessUnits', backref='phone_interview_questions')
    role = db.relationship('Roles', backref='phone_interview_questions')

    __table_args__ = (
        db.Index('idx_phone_q_business_unit_role_pos', 'business_unit_id', 'role_id', 'position'),
        db.Index('idx_phone_q_business_unit', 'business_unit_id'),
    )



# Candidate Interaction History Tables
class PhoneInterviews(db.Model):
    __tablename__ = "phone_interviews"

    interview_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    business_unit_id = db.Column(db.Integer, db.ForeignKey("business_units.business_unit_id", ondelete="CASCADE"), nullable=False)
    elevenlabs_call_id = db.Column(db.String(255), unique=True, nullable=False)
    call_status = db.Column(db.String(50), nullable=False)  # 'completed', 'failed', 'missed', 'scheduled'
    call_duration = db.Column(db.Integer)  # in seconds
    started_at = db.Column(db.DateTime(timezone=True))
    ended_at = db.Column(db.DateTime(timezone=True))
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    ai_score = db.Column(db.Integer)  # AI-generated interview score (1-100)
    ai_recommendation = db.Column(db.String(50))  # 'recommended', 'not_recommended', 'pending_review'
    thread_id_openai = db.Column(db.String(255))  # OpenAI thread ID used for transcript evaluation
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))

    # Relationships
    candidate = db.relationship("Candidates", backref="phone_interviews")
    business_unit = db.relationship("BusinessUnits", backref="phone_interviews")

    __table_args__ = (
        db.Index('idx_phone_interviews_candidate', 'candidate_id'),
        db.Index('idx_phone_interviews_business_unit', 'business_unit_id'),
        db.Index('idx_phone_interviews_vapi_call', 'elevenlabs_call_id'),
        db.Index('idx_phone_interviews_status', 'call_status'),
    )

    def __repr__(self):
        return f'<PhoneInterview {self.interview_id}: candidate_id={self.candidate_id}, status={self.call_status}>'

class WhatsappStatusUpdates(db.Model):
    __tablename__ = 'whatsapp_status_updates'

    id = db.Column(db.Integer, primary_key=True)
    object_type = db.Column(db.String(50))
    entry_id = db.Column(db.BigInteger)
    messaging_product = db.Column(db.String(50))
    wa_id = db.Column(db.String(15))
    phone_number_id = db.Column(db.String(50))
    message_body = db.Column(db.Text)
    conversation_id = db.Column(db.String(50))
    origin_type = db.Column(db.String(50))
    billable = db.Column(db.Boolean)
    pricing_model = db.Column(db.String(50))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20))
    timestamp = db.Column(db.BigInteger)
    field = db.Column(db.String(50))
    status_id = db.Column(db.String(100))
    lag_killed = db.Column(db.Boolean, default=False)
    campaign_id = db.Column(db.String(100))
    error_info = db.Column(db.JSON)

class ScreeningMessages(db.Model):
    __tablename__ = 'screening_messages'
    message_serial = db.Column(db.Integer, primary_key=True)
    wa_id = db.Column(db.String(50))
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id'))
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'))
    message_id = db.Column(db.String(50))
    thread_id = db.Column(db.String(50))
    time_stamp = db.Column(db.DateTime)
    sent_by = db.Column(db.String(50))
    message_body = db.Column(db.Text)
    conversation_type = db.Column(db.String(10))
    whatsapp_msg_id = db.Column(db.String(100))
    set_id = db.Column(db.Integer, db.ForeignKey('question_sets.set_id'))
    question_id = db.Column(db.Integer, db.ForeignKey('screening_questions.question_id'))

    # Relationships
    business_unit = db.relationship("BusinessUnits", backref="screening_messages")
    candidate = db.relationship("Candidates", backref="screening_messages")
    question = db.relationship("ScreeningQuestions", backref="screening_messages")

class CandidateReferences(db.Model):
    __tablename__ = "candidate_references"

    reference_id = db.Column(db.Integer, primary_key=True)
    reference_wa_id = db.Column(db.String(50))
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey("question_sets.set_id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("screening_questions.question_id", ondelete="CASCADE"), nullable=False)
    reach_out_delivered = db.Column(db.Boolean, default=False)
    reference_complete = db.Column(db.Boolean, default=False)
    assessment = db.Column(db.JSON)

    candidate = db.relationship("Candidates", backref="candidate_references", lazy="joined")

class ReferenceMessages(db.Model):
    __tablename__ = "reference_messages"

    message_serial = db.Column(db.Integer, primary_key=True)
    wa_id = db.Column(db.String(50))
    reference_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_references.reference_id", ondelete="CASCADE")
    )
    message_id = db.Column(db.String(50))
    thread_id = db.Column(db.String(50))
    time_stamp = db.Column(db.DateTime)
    sent_by = db.Column(db.String(50))
    message_body = db.Column(db.Text)
    conversation_type = db.Column(db.String(10))
    whatsapp_msg_id = db.Column(db.String(100))

class CandidateMedia(db.Model):
    __tablename__ = "candidate_media"

    media_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.candidate_id", ondelete="CASCADE"))
    business_unit_id = db.Column(db.Integer, db.ForeignKey("business_units.business_unit_id", ondelete="CASCADE"))
    question_id = db.Column(db.Integer, db.ForeignKey("screening_questions.question_id", ondelete="SET NULL"))
    set_id = db.Column(db.Integer)
    string_submission = db.Column(db.Text)
    media_type = db.Column(db.String(50))  # 'image', 'document', 'text', etc.
    media_subtype = db.Column(db.String(50))  # 'INE', 'RFC', 'CURP', etc.
    file_name = db.Column(db.String(255))
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    s3_bucket = db.Column(db.String(100))
    s3_key = db.Column(db.String(500))
    s3_url = db.Column(db.String(1000))
    upload_timestamp = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    whatsapp_media_id = db.Column(db.String(100))
    sha256_hash = db.Column(db.String(100))
    flow_token = db.Column(db.String(100))
    verified = db.Column(db.Boolean, default=False)
    verification_result = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    updated_at = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        db.Index('idx_candidate_media_candidate_id', 'candidate_id'),
        db.Index('idx_candidate_media_business_unit_id', 'business_unit_id'),
        db.Index('idx_candidate_media_question_id', 'question_id'),
        db.Index('idx_candidate_media_upload_timestamp', 'upload_timestamp'),
        db.Index('idx_candidate_media_whatsapp_id', 'whatsapp_media_id'),
        db.Index('idx_candidate_media_business_unit_subtype_string', 'business_unit_id', 'media_subtype', 'string_submission'),
    )

class OnboardingResponses(db.Model):
    __tablename__ = "onboarding_responses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    question = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=True)
    survey = db.Column(db.String, nullable=True)

    __table_args__ = (
        db.Index('idx_onboarding_responses_candidate_id', 'candidate_id'),
    )

class EmailLogs(db.Model):
    __tablename__ = "email_logs"

    id = db.Column(db.BigInteger, primary_key=True)
    recipient_email = db.Column(db.String(320), nullable=False)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete="SET NULL"), nullable=True)
    subject = db.Column(db.Text, nullable=True)
    template_name = db.Column(db.String(150), nullable=True)
    payload = db.Column(db.JSON, nullable=True)
    message_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="sent")
    error_info = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    # Relationships
    business_unit = db.relationship("BusinessUnits", backref="email_logs")

    __table_args__ = (
        db.Index("idx_email_logs_recipient", "recipient_email"),
        db.Index("idx_email_logs_business_unit", "business_unit_id"),
        db.Index("idx_email_logs_sent_at", "sent_at"),
    )


# Performance Tracking Tables
class ResponseTiming(db.Model):
    __tablename__ = 'response_timings'

    id = db.Column(db.Integer, primary_key=True)  # Clave primaria
    employee_id = db.Column(db.Integer, nullable=False)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete="CASCADE"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    time_delta = db.Column(db.Numeric, nullable=False)
    assistant_id = db.Column(db.String(50))
    # Token and model usage fields
    model = db.Column(db.String(50), nullable=False)
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)
    total_tokens = db.Column(db.Integer, nullable=False)

    # Relationships
    business_unit = db.relationship("BusinessUnits", backref="response_timings")

class EligibilityEvaluationLog(db.Model):
    __tablename__ = 'eligibility_evaluation_log'
    
    evaluation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False, index=True)
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.business_unit_id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False, index=True)
    role_name = db.Column(db.String(255), nullable=False)
    
    # AI evaluation result
    is_eligible = db.Column(db.Boolean, nullable=False)
    ai_reasoning = db.Column(db.Text, nullable=True)  # The "reasoning" field from AI response
    raw_ai_response = db.Column(db.JSON, nullable=True)  # Full JSON response from AI
    
    # Questions and answers used for evaluation  
    questions_and_answers = db.Column(db.JSON, nullable=True)  # The input data used
    eligibility_criteria = db.Column(db.JSON, nullable=True)  # Role criteria used
    
    # Manual review fields
    manual_review_status = db.Column(db.String(50), nullable=True, index=True)  # null, 'pending', 'reviewed'
    manual_review_result = db.Column(db.Boolean, nullable=True)  # Manual verification: True/False/null
    manual_review_date = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    evaluation_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    assistant_id = db.Column(db.String(100), nullable=True)  # OpenAI assistant ID used
    thread_id = db.Column(db.String(100), nullable=True)  # OpenAI thread ID
    
    # Relationships
    candidate = db.relationship('Candidates', backref='eligibility_evaluations')
    role = db.relationship('Roles', backref='eligibility_evaluations')
    business_unit = db.relationship('BusinessUnits', backref='eligibility_evaluations')
    
    def __repr__(self):
        return f'<EligibilityLog {self.evaluation_id}: candidate_id={self.candidate_id}, role_id={self.role_id}, eligible={self.is_eligible}>'




# Whatever else we need to add


class AdTemplate(db.Model):
    __tablename__ = 'ad_templates'

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(50), nullable=False)
    key = db.Column(db.String(255), nullable=False, unique=True)
    json_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text("now()"))

    def __repr__(self):
        return f'<AdTemplate {self.id} {self.key}>'

