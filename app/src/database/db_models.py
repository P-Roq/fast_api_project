from typing import (
    Union,
    Any,
    Optional,
    Dict,
    List,
    Iterable,
    )
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    update,
    delete,
    Column,
    Integer,
    Integer,
    Float,
    TEXT,
    DateTime,
    VARCHAR,
    Boolean,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
    )
from sqlalchemy.orm import Session, relationship, joinedload
from sqlalchemy.sql import func, and_, label

from src.database.db_setup import Base, engine
from src.env_models import settings

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True, unique=True,)
    name = Column(VARCHAR(100,), nullable=False,)
    email = Column(VARCHAR(100,), nullable=False, unique=True,)
    password = Column(VARCHAR(100,), nullable=False, unique=True,)
    created_at = Column(DateTime(timezone=True,), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True,), onupdate=func.now(), nullable=True)
    last_login = Column(DateTime, default=datetime.utcnow)


class Posts(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True, autoincrement=True, unique=True,)
    created_at = Column(DateTime, default=datetime.utcnow,)
    updated_at = Column(DateTime(timezone=True,), onupdate=func.now(), nullable=True)
    view_count = Column(Integer,)
    title = Column(TEXT,)
    user_id = Column(
        Integer, 
        ForeignKey('users.user_id', ondelete='CASCADE', name='posts_users_f',),
        nullable=False,
        )
    user_info = relationship('Users', uselist=False)


class Votes(Base):
    __tablename__ = 'votes'
    vote_id = Column(Integer, primary_key=True, autoincrement=True, unique=True,)
    post_id = Column(
        Integer,
        ForeignKey('posts.post_id', ondelete='CASCADE', onupdate='CASCADE', name='votes_posts_f',),
        primary_key=True, 
        nullable=False,
        )
    user_id = Column(
        Integer, 
        ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE', name='votes_users_f',),
        primary_key=True,
        nullable=False,
        )
    created_at = Column(DateTime, default=datetime.utcnow,)
    updated_at = Column(DateTime(timezone=True,), onupdate=func.now(), nullable=True)


class SocialGroups(Base):
    __tablename__ = 'social_groups'
    group_id = Column(Integer, primary_key=True, autoincrement=True, unique=True,)
    admin_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE', name='social_groups_users_f',),
        primary_key=True,
        )
    title = Column(VARCHAR(100,), nullable=False, unique=True)
    details = Column(TEXT, nullable=False,)
    created_at = Column(DateTime(timezone=True,), default=datetime.utcnow, nullable=False,)
    updated_at = Column(DateTime(timezone=True,), onupdate=func.now(), nullable=True,)
    admin_info = relationship('Users', uselist=False)
    members_info = relationship('GroupMembers', uselist=False)
    __table_args__ = (
        PrimaryKeyConstraint('group_id', 'admin_id', name='social_groups_p'),
        UniqueConstraint('group_id', 'admin_id', name='group_user_u'),
    )


class GroupMembers(Base):
    __tablename__ = 'group_members'    
    member_id = Column(Integer, primary_key=True, autoincrement=True, unique=True,)
    created_at = Column(DateTime, default=datetime.utcnow,)
    updated_at = Column(DateTime(timezone=True,), onupdate=func.now(), nullable=True,)
    admin = Column(Boolean, nullable=False, default=False)
    user_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE', name='group_members_users_f',),
        primary_key=True,
        nullable=False,
        )
    group_id = Column(
        Integer,
        ForeignKey('social_groups.group_id', ondelete='CASCADE', name='group_members_social_groups_f',),
        primary_key=True,
        nullable=False,
        )

    __table_args__ = (
        PrimaryKeyConstraint('member_id', 'user_id', 'group_id', name='group_members_p'),
        UniqueConstraint('user_id', 'group_id', name='user_group_u'),
    )
    
#-----------------------------------------------------------------------------------------------------------------------


@dataclass
class DBSession:
    def __init__(self, session_local, Table,):
        self.SessionLocal = session_local
        self.Table = Table

    @property
    def fetch_last_created(self,):
        newest_resource = (
            self.SessionLocal
            .query(self.Table)
            .order_by(self.Table.created_at.desc())
            .first()
            )
        return newest_resource


    @property
    def fetch_last_updated(self,):
        newest_resource = (
            self.SessionLocal
            .query(self.Table)
            .order_by(self.Table.updated_at.desc())
            .first()
            )
        return newest_resource


    def all_resources(
            self,
            search_column: str, 
            relationships: List[str] = None,
            limit: Optional[int] = None,
            skip: Optional[int] = None,
            search: Optional[str] = "",
            ) -> list:
        
        search_attr = getattr(self.Table, search_column)

        if relationships:

            join_attributes = [getattr(self.Table, relationship_attr) for relationship_attr in relationships]
            join_attributes = [joinedload(relationship_attr) for relationship_attr in join_attributes]

            all_resources = (
                self.SessionLocal
                .query(self.Table)
                .filter(search_attr.contains(search))
                .limit(limit)
                .offset(skip)
                .options(*join_attributes)
                .all()
                )
        else:
            all_resources = (
                self.SessionLocal
                .query(self.Table)
                .filter(search_attr.contains(search))
                .limit(limit)
                .offset(skip)
                .all()
                )

        all_resources_cleaned = [
            {key: value for key, value in resource.__dict__.items() if not key.startswith('_')} for resource in all_resources
            ]
        if len(all_resources_cleaned) == 0:
            return None
        else:
            return all_resources_cleaned
    
    
    def unique_values(self, column_name: str) -> list:
        attribute = getattr(self.Table, column_name)
        unique_values = self.SessionLocal.query(attribute).distinct().all()
        unique_values = [row[0] for row in unique_values] 
        return unique_values

    
    def fetch_resource(self, columns_values: Dict[str, str], convert_to_dict: bool = False) -> dict:
        """Fetch a full resource/row based on a column and its value. The input `columns_values` is a 
        dictionary whose a single item is a {column: value} in the database table, that will serve to
        filter out/find the correct resource; this dictionary, can take as much items as the number of
        fields in the table. 
        """
        
        items = columns_values.items()
        filter_attributes = [getattr(self.Table, item[0]) == item[1] for item in items]

        row = (
            self.SessionLocal
            .query(self.Table)
            .filter(and_(*filter_attributes))
            .first()
            )
        
        if row and convert_to_dict:
            row = {column.name: getattr(row, column.name) for column in self.Table.__table__.columns}

        return row


    def fetch_grouped_resources(self, id_column: str, id: int, join_column: str = False) -> list:
        
        attribute = getattr(self.Table, id_column)

        if join_column:
            join_attribute = getattr(self.Table, join_column)

            user_resources = (
                self.SessionLocal
                .query(self.Table)
                .options(joinedload(join_attribute))
                .filter(attribute == id)
                .all()
                )
        else:
            user_resources = (
                self.SessionLocal
                .query(self.Table)
                .filter(attribute == id)
                .all()
                )
             
        user_resources_cleaned = [
            {key: value for key, value in resource.__dict__.items() if not key.startswith('_')} for resource in user_resources
            ]
        return user_resources_cleaned
    

    def fetch_value_by_unique_value(self, column_unique: str, column_target: str, value_to_match: Any):

        attribute_find_row = getattr(self.Table, column_unique)
        attribute_find_column = getattr(self.Table, column_target)

        value = (
            self.SessionLocal
            .query(attribute_find_column)
            .filter(attribute_find_row == value_to_match)
            .first()
            )
        
        if isinstance(value, tuple):
            return value[0] # the value is inside a tuple
        else:
            return value


    def add_resource(self, dump: dict) -> None:
        
        new_resource = self.Table(**dump)
        try:
            self.SessionLocal.begin()
            self.SessionLocal.add(new_resource)
            self.SessionLocal.commit()
        except:
            self.SessionLocal.rollback()
            self.SessionLocal.begin()
            self.SessionLocal.add(new_resource)
            self.SessionLocal.commit()
        return
    
    
    def update_resource(self, id_column: str, id: int, dump: dict,) -> None:
        """This function can be used to either update or patch a resource.
        """

        (
        self.SessionLocal
        .query(self.Table)
        .filter(getattr(self.Table, id_column) == id)
        .update(dump)
        )
        
        return 
    

    def delete_resource(self, columns_values: Dict[str, str],) -> None:
        
        items = columns_values.items()
        filter_attributes = [getattr(self.Table, item[0]) == item[1] for item in items]
        
        (
        self.SessionLocal
        .query(self.Table)
        .filter(and_(*filter_attributes))
        .delete()
        )
        return

#--------------------------------------------------------------------------------------------------------------------

@dataclass
class DBSessionPosts(DBSession):
    def __init__(self, session_local, Table=Posts,):
        # Call the constructor of the Base class (DBSession).
        super().__init__(session_local, Table)

    def get_upvotes_by_post(self, post_id: int) -> int:
        post_votes = (
            self.SessionLocal
            .query(self.Table, func.count(Votes.post_id).label('upvotes'))
            .join(
                Votes, Votes.post_id == self.Table.post_id,
                isouter=False,
            )
            .group_by(self.Table.post_id)
            .filter(self.Table.post_id==post_id)
            .first()
            )
        
        if post_votes:
            return post_votes[1] # value inside a tuple
        else: 
            return 0 # if there are no upvotes for this post return `0`.
    

    def all_posts(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = "",
        filter_columns: Dict[str, Any] = None,
        ) -> list:

        filter_container = [self.Table.title.contains(search)]
        
        if filter_columns:
            items = filter_columns.items()
            filter_attributes = [getattr(self.Table, item[0]) == item[1] for item in items]

            filter_container = filter_container + filter_attributes

        all_resources = (
            self.SessionLocal
            .query(
                self.Table,
                label('upvotes', func.count(Votes.post_id))
                )
            .join(
                Votes, Votes.post_id == self.Table.post_id,
                isouter=True
                )
            .filter(
                and_(*filter_container)
                )
            .options(
                joinedload(self.Table.user_info),
                )
            .group_by(self.Table.post_id)
            .limit(limit)
            .offset(skip)
            .all()
            )

        organized_results = []

        for row in all_resources:
            post_dict = {
                'post_id': row[0].post_id,
                'view_count': row[0].view_count,
                'user_id': row[0].user_id,
                'title': row[0].title,
                # 'score': row[0].score,
                'created_at': row[0].created_at,
                'updated_at': row[0].updated_at,
                'author': row[0].user_info.name,
                'email': row[0].user_info.email,
                # SQLAlchemy is not providing a name to 'upvotes' despite of setting 
                # setting `label('upvotes', func.count(Votes.post_id))` for `all_resources`.
                'upvotes': row[1]  
            }
            
            organized_results.append(post_dict)

        return organized_results


#--------------------------------------------------------------------------------------------------------------------


@dataclass
class DBSessionUsers(DBSession):
    def __init__(self, session_local, Table=Users,):
        super().__init__(session_local, Table)

    def fetch_user_info(self, id_column: str, id_value: Any) -> list:
    
        identification_attribute = getattr(self.Table, id_column)
        find_user = identification_attribute == id_value

        try:
            # If the user has no posts this query will return a null value.
            user_info = (
                self.SessionLocal
                .query(self.Table, func.count(Posts.post_id).label('posts'))
                .join(
                    self.Table, self.Table.user_id == Posts.user_id,
                    isouter=True,
                    )
                .group_by(Posts.user_id)
                .filter(find_user)
                .first()
                )

            organized_results = {
                    'user_id': user_info[0].user_id,
                    'name': user_info[0].name,
                    'email': user_info[0].email,
                    'posts': user_info[1],
                    'created_at': user_info[0].created_at,
                    'updated_at': user_info[0].updated_at,
                    'last_login': user_info[0].last_login,
                }

        except:
            user_info = (
                self.SessionLocal
                .query(self.Table,)
                .filter(find_user)
                .first()
                )

            organized_results = {
                    'user_id': user_info.user_id,
                    'name': user_info.name,
                    'email': user_info.email,
                    'posts': 0,
                    'created_at': user_info.created_at,
                    'updated_at': user_info.updated_at,
                    'last_login': user_info.last_login,
                }

        return organized_results


#--------------------------------------------------------------------------------------------------------------------


@dataclass
class DBSessionSocialGroups(DBSession):
    def __init__(self, session_local, Table=SocialGroups,):
        super().__init__(session_local, Table)

    def count_members_by_social_group(self, group_id: int) -> int:
        groups_members = (
            self.SessionLocal
            .query(self.Table, func.count(GroupMembers.group_id).label('members'))
            .join(
                GroupMembers, GroupMembers.group_id == self.Table.group_id,
                isouter=False,
            )
            .group_by(self.Table.group_id)
            .filter(self.Table.group_id==group_id)
            .first()
            )
        
        return groups_members[1] # A group has always at least one member (the admin). 
    

    def all_social_groups(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = "",
        filter_columns: Dict[str, Any] = None,
        ) -> list:

        filter_container = [self.Table.title.contains(search)]

        if filter_columns:
            items = filter_columns.items()
            filter_attributes = []

            for item in items:
                if isinstance(item[1], Iterable):
                    attribute_condition = getattr(self.Table, item[0]).in_(item[1])
                else:
                    attribute_condition = getattr(self.Table, item[0])
                filter_attributes.append(attribute_condition)
        
            filter_container = filter_container + filter_attributes

        all_resources = (
            self.SessionLocal
            .query(
                self.Table,
                func.count(GroupMembers.group_id).label('members')
                )
            .join(
                GroupMembers, GroupMembers.group_id == self.Table.group_id,
                isouter=True
                )
            .options(
                joinedload(self.Table.admin_info),
                )
            .filter(and_(*filter_container))
            .group_by(self.Table.group_id)
            .offset(skip)
            .limit(limit)
            .all()
            )

        organized_results = []
        
        for row in all_resources:
            post_dict = {
                "group_id": row[0].group_id,
                "details": row[0].details,
                "created_at": row[0].created_at,
                "updated_at": row[0].updated_at,
                "title": row[0].title,
                "admin_info": row[0].admin_info,
                "members": row[1],
                }
            
            organized_results.append(post_dict)

        return organized_results
    

    def fetch_social_group_members(self, user_id: int,) -> list:

        social_groups_id = (
            self.SessionLocal
            .query(
                GroupMembers,
                )
            .filter(GroupMembers.user_id == user_id)
            .all()
        )

        social_groups_id = [resource.group_id for resource in social_groups_id]

        
        return self.all_social_groups(
            filter_columns={'group_id': social_groups_id}
            )
    

#--------------------------------------------------------------------------------------------------------------------

@dataclass
class DBSessionGroupMembers(DBSession):
    def __init__(self, session_local, Table=GroupMembers,):
        super().__init__(session_local, Table)


    def get_all_members_by_group(self, id_column: str, id_value: Any) -> list:
    
        identification_attribute = getattr(self.Table, id_column)
        find_group = identification_attribute == id_value

        group_members = (
            self.SessionLocal
            .query(Users, GroupMembers)
            .join(
                self.Table, self.Table.user_id == Users.user_id,
                isouter=False,
                )
            .filter(find_group)
            .all()
            )
        
        organized_results = []
        
        for row in group_members:
            post_dict = {
                "user_id": row[0].user_id,
                "name": row[0].name,
                "member_id": row[1].member_id,
                "admin": row[1].admin,
                }
            
            organized_results.append(post_dict)

        return organized_results