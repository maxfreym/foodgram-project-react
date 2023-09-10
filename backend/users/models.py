from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CustomFollow(models.Model):
    """Подписка"""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following_follows",
        verbose_name="Подписчик",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower_follows",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "follower",
                    "following",
                ),
                name="unique_customfollow",
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="self_subscription_prohibited",
            ),
        )

    def __str__(self):
        return f"{self.follower} подписан на {self.following}"
