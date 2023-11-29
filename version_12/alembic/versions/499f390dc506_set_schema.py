"""set schema

Revision ID: 499f390dc506
Revises: 
Create Date: 2023-11-29 12:35:57.633212

"""
from typing import Sequence, Union
from datetime import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '499f390dc506'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(    
        'users',
        sa.Column('user_id', sa.Integer, autoincrement=True, unique=True,),
        sa.Column('name', sa.VARCHAR(100,), nullable=False,),
        sa.Column('email', sa.VARCHAR(100,), nullable=False, unique=True,),
        sa.Column('password', sa.VARCHAR(100,), nullable=False, unique=True,),
        sa.Column('created_at', sa.DateTime(timezone=True,), default=datetime.utcnow, nullable=False,),
        sa.Column('updated_at', sa.DateTime(timezone=True,), onupdate=sa.func.now(), nullable=True,),
        sa.Column('last_login', sa.DateTime, nullable=True,),
        sa.PrimaryKeyConstraint('user_id')
        )


    op.create_table(
        'posts',
        sa.Column('post_id', sa.Integer, autoincrement=True, unique=True,),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow,),
        sa.Column('updated_at', sa.DateTime(timezone=True,), onupdate=sa.func.now(), nullable=True,),
        sa.Column('view_count', sa.Integer,),
        sa.Column('title', sa.TEXT,),
        sa.Column('user_id', 
            sa.Integer, 
            sa.ForeignKey(column='users.user_id', ondelete='CASCADE', name='posts_users_fk',),
            nullable=False,
            ),
        sa.PrimaryKeyConstraint('post_id')
        )
    


    op.create_table(
        'votes',
        sa.Column('vote_id', sa.Integer, autoincrement=True, unique=True,),
        sa.Column('post_id', 
            sa.Integer,
            sa.ForeignKey(column='posts.post_id', ondelete='CASCADE', onupdate='CASCADE', name='votes_posts_fk',),
            nullable=False,
            ),
        sa.Column('user_id', 
            sa.Integer, 
            sa.ForeignKey(column='users.user_id', ondelete='CASCADE', onupdate='CASCADE', name='votes_users_fk',),
            nullable=False,
            ),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow,),
        sa.Column('updated_at', sa.DateTime(timezone=True,), onupdate=sa.func.now(), nullable=True,),
        sa.PrimaryKeyConstraint('vote_id', 'post_id', 'user_id'),
        )
    


    op.create_table(
        'social_groups',
        sa.Column('group_id', sa.Integer, primary_key=True, autoincrement=True, unique=True),
        sa.Column(
            'admin_id',
            sa.Integer,
            sa.ForeignKey('users.user_id', ondelete='CASCADE', name='social_groups_users_fk'),
            primary_key=True,
            unique=True
            ),
        sa.Column('title', sa.VARCHAR(100), nullable=False, unique=True),
        sa.Column('details', sa.TEXT, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('group_id', 'admin_id', name='social_groups_pk'),
        sa.UniqueConstraint('group_id', 'admin_id', name='group_admin_uc'),
    )
    

    op.create_table(
        'group_members',
        sa.Column('member_id', sa.Integer, primary_key=True, autoincrement=True, unique=True,),
        sa.Column(
            'user_id',
            sa.Integer,
            sa.ForeignKey('users.user_id', ondelete='CASCADE', name='group_members_users_fk'),
            primary_key=True,
            ),
        sa.Column(
            'group_id',
            sa.Integer,
            sa.ForeignKey('social_groups.group_id', ondelete='CASCADE', name='group_members_social_groups_fk'),
            primary_key=True,
            ),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow,),
        sa.Column('updated_at', sa.DateTime(timezone=True,), onupdate=sa.func.now(), nullable=True,),
        sa.Column('admin',  sa.Boolean, nullable=False, default=False),
        sa.PrimaryKeyConstraint('member_id', 'user_id', 'group_id', name='group_members_pk'),
        sa.UniqueConstraint('user_id', 'group_id', name='_user_group_uc'),
    )


def downgrade() -> None:


    # Drop foreign key constraints
    op.drop_constraint('posts_users_fk', 'posts', type_='foreignkey',)
    op.drop_constraint('votes_posts_fk', 'votes', type_='foreignkey',)
    op.drop_constraint('votes_users_fk', 'votes', type_='foreignkey',)
    op.drop_constraint('social_groups_users_fk', 'social_groups', type_='foreignkey',)
    op.drop_constraint('group_members_users_fk', 'group_members', type_='foreignkey',)
    op.drop_constraint('group_members_social_groups_fk', 'group_members', type_='foreignkey',)

    # Drop tables.
    op.drop_table('posts')
    op.drop_table('users')
    op.drop_table('votes')
    op.drop_table('social_groups')
    op.drop_table('group_members')