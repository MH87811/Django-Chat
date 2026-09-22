from .models import Conversation, ConversationMember
from django.db import transaction
from django.db.models import Count


class ConversationService:
    PRIVATE_TYPE = Conversation.TypeChoices.PRIVATE
    GROUP_TYPE = Conversation.TypeChoices.GROUP
    MEMBER_ROLE = ConversationMember.RoleChoices.MEMBER
    ADMIN_ROLE = ConversationMember.RoleChoices.ADMIN

    def __create_conversation(self, conversation_type, title=''):
        if conversation_type not in Conversation.TypeChoices.choices:
            raise ValueError('invalid Conversation Type')
        conversation = Conversation.objects.create(
            title=title,
            type=conversation_type,
        )
        return conversation

    def add_member(self, conversation, member, role):
        return ConversationMember.objects.get_or_create(
            conversation=conversation,
            user=member,
            defaults={
                'role': self.MEMBER_ROLE if not role else role,
            },
        )

    def add_members(self, conversation, members):
        user_ids = {member.id for member in members}
        existing_user_ids = set(
            ConversationMember.objects.filter(
                conversation=conversation,
                user_id__in=user_ids,
            ).values_list("user_id", flat=True)
        )

        new_user_ids = user_ids - existing_user_ids

        memberships = [
            ConversationMember(
                conversation=conversation,
                user_id=user_id,
                role=self.MEMBER_ROLE,
            )
            for user_id in new_user_ids
        ]

        return ConversationMember.objects.bulk_create(memberships)

    def create_private_chat(self, users):
        users = set(users)

        if not len(users) == 2:
            raise ValueError('Invalid User Input for PRIVATE Conversation')

        user_1, user_2 = users

        existing_conversation = Conversation.objects.filter(
                type=self.PRIVATE_TYPE,
                members__user=user_1,
            ).filter(
                members__user=user_2,
            )

        if existing_conversation.exists():
            raise ValueError('Private Conversation already exists')

        with transaction.atomic():
            conversation = self.__create_conversation(conversation_type=self.PRIVATE_TYPE)
            self.add_members(conversation, users)
        return conversation


    def create_group_chat(self, admin, members, title):
        members = set(members)
        members.add(admin)

        member_ids = {user.pk for user in members}

        existing_conversations = Conversation.objects.filter(
            type=self.GROUP_TYPE,
            title=title,
            members__user__in=member_ids,
        ).annotate(
            member_count=Count("members", distinct=True),
        ).filter(
            member_count=len(member_ids)
        )

        for conversation in existing_conversations:
            existing_member_ids = set(
                conversation.members.values_list(
                    "user_id",
                    flat=True,
                )
            )

            if existing_member_ids != member_ids:
                continue

            if existing_member_ids == member_ids:
                if conversation.members.filter(
                        user=admin,
                        role=self.ADMIN_ROLE,
                ).exists():
                    raise ValueError("Group already exists")
        members.discard(admin)

        with transaction.atomic():
            conversation = self.__create_conversation(
                conversation_type=self.GROUP_TYPE,
                title=title,
            )
            self.add_member(
                conversation=conversation,
                member=admin,
                role=self.ADMIN_ROLE,
            )
            self.add_members(
                conversation=conversation,
                members=members,
            )
            return conversation

    def remove_member(self):
        ...