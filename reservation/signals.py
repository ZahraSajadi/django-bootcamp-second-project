from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


def reservation_post_delete_cancell_email(sender, instance, **kwargs):
    users = User.objects.filter(team=instance.team).all()
    for user in users:
        subject = "Meeting Cancelled"
        message = f"""{user.first_name} {user.last_name}, please note,
        reservation for your team's meeting
        from {instance.start_date} to {instance.end_date} in {instance.room} has been CANCELLED."""
        recipient = user.email
        send_mail(
            subject,
            message,
            recipient_list=(recipient,),
            from_email="noreply@unchained.com",
        )
