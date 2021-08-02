import graphene
import channels_graphql_ws

from .types import SnippetType

from django.conf import settings


# ------------------------------------------------------------------------ SUBSCRIPTIONS

class OnSnippetTransaction(channels_graphql_ws.Subscription):
    """
A group is like a chat room; if you are subscribed to that room, you get
the updates. In this case, the broadcast_group is CREATE, UPDATE, or DELETE.
    """

    # These are what can be returned to the subscription.
    broadcast_group = graphene.String()  # e.g. CREATE, UPDATE, DELETE
    sender = graphene.String()
    snippet = graphene.Field(lambda: SnippetType)
    ok = graphene.Boolean()

    # Input arguments sent via GraphQL from the client.
    # Currently keyed-on by the API, e.g. from a mutation.
    class Arguments:
        broadcast_group = graphene.String(required=False,
                                          default_value=None)  # This is the type of event the client wants

    # Client subscription handler
    def subscribe(self, info, broadcast_group=None, *args, **kwds):
        # print("Context [{}]".format(info.context))
        del info

        # Returns the list or tuple of subscription group names
        # to which this client has subscribed.
        # (I dunno who called this, though.)
        return [broadcast_group] if broadcast_group is not None else None

    def unsubscribe(self, info, broadcast_group=None, *args, **kwds):
        print("unsubscribe arg was [{}]".format(broadcast_group))

        print("You are unsubscribed")

    # This method invoked each time subscription "triggers".
    # ANTHONY - For some reason, this only fires if an argument is supplied,
    # even though the argument is not required.
    # Note: the first argument receives the payload/root.
    def publish(self, info, broadcast_group, *args, **kwds):
        """
The publish method is invoked each time data is triggered to the subscription.
The data passed through here. Fields set for the class can be set on the return().
        """

        # The `self` object contains payload delivered from the `broadcast()`.
        # Writing it out as variables to remind of that fact.
        new_msg_sender = self["sender"]
        new_msg_snippet = self["snippet"]

        # Avoid self-notifications.
        if (
                info.context.user.is_authenticated
                and new_msg_sender == info.context.user.username
        ):
            return OnSnippetTransaction.SKIP

        if settings.DEBUG:
            print("publish returning [{},{},{}]".format(broadcast_group, new_msg_sender, new_msg_snippet))
        return OnSnippetTransaction(
            broadcast_group=broadcast_group, sender=new_msg_sender, snippet=new_msg_snippet, ok=True
        )

    # Auxiliary function to send subscription notifications.
    # Might be called from a mutation, e.g.
    @classmethod
    def snippet_event(cls, broadcast_group, sender, snippet):
        if settings.DEBUG:
            print("snippet_event [{},{},{}]".format(broadcast_group, sender, snippet))

        # Call broadcast to notify all subscriptions in the group.
        # Sending to group = None means all the subscriptions of type will be triggered.
        cls.broadcast(
            group=broadcast_group,
            payload={"sender": sender, "snippet": snippet},
        )


class OnSnippetNoGroup(channels_graphql_ws.Subscription):
    """
A group is like a chat room; if you are subscribed to that room, you get
the updates.

This class defines a means to get ALL changes, w/o subscribing to a
specific group. Thus, monitoring this subscription gets updates to
CREATE, UPDATE, or DELETE.
    """

    # These are what can be returned to the subscription.
    # In this case, I specifically don't have a broadcast_group as the type.
    trans_type = graphene.String()  # e.g. CREATE, UPDATE, DELETE
    sender = graphene.String()
    snippet = graphene.Field(lambda: SnippetType)
    ok = graphene.Boolean()

    # Input arguments sent via GraphQL from the client.
    # Currently keyed-on by the API, e.g. from a mutation.
    class Arguments:
        # trans_type = graphene.String()
        pass

    def subscribe(self, info, *args, **kwds):
        # print("Context [{}]".format(info.context))
        del info

        # Returns the list or tuple of subscription group names
        # to which this client has subscribed.
        # (I dunno who called this, though.)
        return None

    def unsubscribe(self, info, *args, **kwds):
        print("You are unsubscribed")

    # ANTHONY - For some reason, this only fires if an argument is supplied,
    # even though the argument is not required.
    #
    # Note: the first argument, self, receives the payload/root.
    def publish(self, info, *args, **kwds):
        """
The publish method is invoked each time data is triggered to the subscription.
The data passed through here. Fields set for the class can be set on the return().
        """

        # The `self` object contains payload delivered from the `broadcast()`.
        # Writing it out as variables to remind of that fact.
        new_msg_sender = self["sender"]
        new_msg_snippet = self["snippet"]
        new_msg_trans_type = self["trans_type"]

        # Avoid self-notifications
        # There won't be a user during pytest unit tests.
        if (
                hasattr(info.context, "user") and
                info.context.user.is_authenticated
                and new_msg_sender == info.context.user.username
        ):
            print("Avoiding self-notification")
            return OnSnippetNoGroup.SKIP

        if settings.DEBUG:
            print("publish returning [{},{}]".format(new_msg_sender, new_msg_snippet))
        return OnSnippetNoGroup(
            sender=new_msg_sender, snippet=new_msg_snippet, ok=True, trans_type=new_msg_trans_type
        )

    # Auxiliary function to send subscription notifications.
    # Might be called from a mutation, e.g.
    @classmethod
    def snippet_event(cls, trans_type, sender, snippet):
        if settings.DEBUG:
            print("snippet_event [{},{},{}]".format(trans_type, sender, snippet))

        # Call broadcast to notify all subscriptions in the group.
        # Sending to group = None means all the subscriptions of type will be triggered.
        cls.broadcast(
            payload={"sender": sender, "snippet": snippet, "trans_type": trans_type},
        )


# GraphQL subscription
class Subscription(graphene.ObjectType):
    # This is how you call from GraphiQL.
    # Remember to use CamelCase, though.
    on_snippet_event = OnSnippetTransaction.Field()
    on_snippet_no_group = OnSnippetNoGroup.Field()
