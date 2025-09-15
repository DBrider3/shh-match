"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kakao_user_id', sa.Text(), nullable=False),
        sa.Column('phone_verified', sa.Boolean(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('banned', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kakao_user_id')
    )

    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nickname', sa.String(), nullable=False),
        sa.Column('gender', sa.String(length=1), nullable=False),
        sa.Column('birth_year', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('job', sa.String(), nullable=True),
        sa.Column('intro', sa.Text(), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=False),
        sa.Column('visible', sa.JSON(), nullable=False),
        sa.CheckConstraint("gender IN ('M', 'F')", name='check_gender'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Create preferences table
    op.create_table(
        'preferences',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_gender', sa.String(length=1), nullable=False),
        sa.Column('age_min', sa.Integer(), nullable=False),
        sa.Column('age_max', sa.Integer(), nullable=False),
        sa.Column('regions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('blocks', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.CheckConstraint("target_gender IN ('M', 'F')", name='check_target_gender'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Create exposure_log table
    op.create_table(
        'exposure_log',
        sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('seen_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_week', sa.String(), nullable=False),
        sa.Column('score', sa.DECIMAL(precision=6, scale=3), nullable=True),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('responded', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'target_user_id', 'batch_week', name='unique_recommendation_per_week')
    )

    # Create likes table
    op.create_table(
        'likes',
        sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('from_user', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_user', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_week', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['from_user'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_user'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_user', 'to_user', 'batch_week', name='unique_like_per_week')
    )

    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_a', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_b', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'active', 'closed')", name='check_status'),
        sa.ForeignKeyConstraint(['user_a'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_b'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('depositor_name', sa.String(), nullable=True),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.CheckConstraint("method IN ('transfer')", name='check_payment_method'),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id')
    )

    # Create admin_actions table
    op.create_table(
        'admin_actions',
        sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=True),
        sa.Column('detail', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reporter', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reported', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('handled', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['reported'], ['users.id']),
        sa.ForeignKeyConstraint(['reporter'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_recs_user_week', 'recommendations', ['user_id', 'batch_week'])
    op.create_index('idx_exposure_user', 'exposure_log', ['user_id', 'seen_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_exposure_user', table_name='exposure_log')
    op.drop_index('idx_recs_user_week', table_name='recommendations')

    # Drop tables in reverse order
    op.drop_table('reports')
    op.drop_table('admin_actions')
    op.drop_table('payments')
    op.drop_table('matches')
    op.drop_table('likes')
    op.drop_table('recommendations')
    op.drop_table('exposure_log')
    op.drop_table('preferences')
    op.drop_table('profiles')
    op.drop_table('users')