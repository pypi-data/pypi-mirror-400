from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from djangoldp.models import Model
from djangoldp.views.ldp_viewset import LDPViewSet
from djangoldp.views.commons import JSONLDParser, JSONLDRenderer
from datetime import datetime


class JobOffersCurrentViewset(LDPViewSet):
    def get_queryset(self):
        return super().get_queryset() \
                      .filter(closingDate__gte=datetime.now())


class JobOffersExpiredViewset(LDPViewSet):
    def get_queryset(self):
        return super().get_queryset() \
                      .filter(closingDate__lte=datetime.now())


class JobOfferServerNotificationView(APIView):
    '''
    A view to dispatch a notification to all users on this server
    From requirement that I want to be notified of all JobOffers matching my skills,
    if my server has set up a subscription to this endpoint
    '''
    permission_classes = (AllowAny,)
    parser_classes = (JSONLDParser,)
    renderer_classes = (JSONLDRenderer,)

    def post(self, request, *args, **kwargs):
        from djangoldp_notification.models import Notification
        from djangoldp_notification.views import filter_object_is_permitted
        from djangoldp_joboffer.models import JobOffer
        from djangoldp_joboffer.serializers import JobOfferModelSerializer
        
        data = request.data

        if 'object' in data:
            try:
                # to send one Notification to many users, we will duplicate the post content
                # for each user and create with many=True
                object_urlid = data['object']['@id'] \
                    if (not isinstance(data['object'], str) and '@id' in data['object']) \
                     else data['object']

                # create a backlinked version of the JobOffer passed, if one does not exist
                if not isinstance(data['object'], str):
                    try:
                        job_offer = JobOffer.objects.get(urlid=object_urlid)
                    except JobOffer.DoesNotExist:
                        job_offer = JobOffer(urlid=object_urlid)

                    serializer = JobOfferModelSerializer(job_offer, data=data['object'])

                    if not serializer.is_valid():
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    serializer.save()

                # only notify local users who have not been notified before
                prior_notified_users = Notification.objects.filter(object=object_urlid).values_list('user', flat=True)
                recipients = get_user_model().objects.exclude(pk__in=prior_notified_users)
                internal_ids = [x.pk for x in recipients if not Model.is_external(x)]

                for recipient in recipients.filter(pk__in=internal_ids):
                    # if the recipient has an appropriate skill for the joboffer
                    if filter_object_is_permitted(recipient, data):

                        summary = data['summary'] if 'summary' in data else ''

                        Notification.objects.create(user=recipient, object=object_urlid, author=data['author'], type=data['type'], summary=summary)

                # return super().create(request, *args, **kwargs)
                return Response(status=status.HTTP_201_CREATED)

            except ImportError:
                return Response("Notifications are not supported by this server", status=status.HTTP_404_NOT_FOUND)
