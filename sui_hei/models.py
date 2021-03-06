import re

from django.contrib.auth.models import (AbstractBaseUser, AbstractUser,
                                        BaseUserManager)
from django.db import connections, models
from django.db.models import CASCADE, DO_NOTHING, SET_NULL, Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Award(models.Model):
    name = models.CharField(max_length=255, null=False)
    groupName = models.CharField(max_length=255, null=False, default="default")
    description = models.TextField(default="")

    class Meta:
        verbose_name = _("Award")

    def __str__(self):
        return self.name


class AwardApplication(models.Model):
    award = models.ForeignKey(Award, on_delete=CASCADE)
    applier = models.ForeignKey("User", related_name="applier", on_delete=CASCADE)
    status = models.IntegerField(_("status"), default=0, null=False)
    comment = models.TextField(_("comment"), null=True)
    reviewer = models.ForeignKey("User", related_name="reviewer", on_delete=CASCADE, null=True)
    created = models.DateTimeField(_("created"), default=timezone.now)
    reviewed = models.DateTimeField(_("reviewed"), null=True)

    class Meta:
        verbose_name = _("Award Application")
        permissions = (
            ("can_review_award_application", _("Can review award application")),
        )

    def __str__(self):
        return "[%s]: %s" % (str(self.applier), str(self.award))

awardapplication_status_enum = {
    0: _("Waiting"),
    1: _("Accepted"),
    2: _("Denied"),
}


class User(AbstractUser):
    nickname = models.CharField(
        _('nick_name'), max_length=255, null=False, unique=True)
    profile = models.TextField(_('profile'), default="")
    current_award = models.ForeignKey(
        "UserAward",
        null=True,
        on_delete=SET_NULL,
        related_name="current_award")
    credit = models.IntegerField(_('credit'), default=0)
    hide_bookmark = models.BooleanField(_('hide bookmark'), default=True)

    REQUIRED_FIELDS = ['nickname']

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def __str__(self):
        return self.nickname


class UserAward(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    award = models.ForeignKey(Award, on_delete=CASCADE)
    created = models.DateField(_("created"), null=False, default=timezone.now)

    class Meta:
        verbose_name = _("User-Award")

    def __str__(self):
        return "[%s] owns [%s]" % (self.user.nickname, self.award)


class Puzzle(models.Model):
    '''
    genre:
      0: umigame
      1: tobira
      2: kameo
      3: shin-keshiki
    '''
    id = models.AutoField(max_length=11, null=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=CASCADE)
    title = models.CharField(_('title'), max_length=255, null=False)
    yami = models.BooleanField(_('yami'), default=False, null=False)
    genre = models.IntegerField(_('genre'), default=0, null=False)
    content = models.TextField(_('content'), null=False)
    solution = models.TextField(_('solution'), null=False)
    created = models.DateTimeField(_('created'), null=False)
    modified = models.DateTimeField(_('modified'), null=False)
    status = models.IntegerField(_('status'), default=0, null=False)
    memo = models.TextField(_('memo'), default="")
    score = models.FloatField(_('score'), default=0, null=False)

    class Meta:
        verbose_name = _("Puzzle")

    def __str__(self):
        return self.title


puzzle_genre_enum = {
    0: _("Albatross"),
    1: _("20th-Door"),
    2: _("Little Albat"),
    3: _("Others & Formal")
}

puzzle_status_enum = {
    0: _("Unsolved"),
    1: _("Solved"),
    2: _("Dazed"),
    3: _("Hidden"),
    4: _("Forced Hidden")
}


class Dialogue(models.Model):
    id = models.AutoField(max_length=11, null=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=CASCADE)
    question = models.TextField(_('question'), null=False)
    questionEditTimes = models.IntegerField(
        _("question edit times"), null=False, default=0)
    answer = models.TextField(_('answer'), null=True)
    answerEditTimes = models.IntegerField(
        _("answer edit times"), null=False, default=0)
    good = models.BooleanField(_('good_ques'), default=False, null=False)
    true = models.BooleanField(_('true_ques'), default=False, null=False)
    created = models.DateTimeField(_('created'), null=False)
    answeredtime = models.DateTimeField(_('answeredtime'), null=True)

    class Meta:
        verbose_name = _("Question")

    def __str__(self):
        return "[%s]%s: {%s} puts {%50s}" % (self.puzzle.id, self.puzzle,
                                             self.user, self.question)


class Hint(models.Model):
    id = models.AutoField(max_length=11, null=False, primary_key=True)
    puzzle = models.ForeignKey(Puzzle, on_delete=CASCADE)
    content = models.TextField(_('content'), null=False)
    created = models.DateTimeField(
        _('created'), null=False, default=timezone.now)

    class Meta:
        verbose_name = _("Hint")

    def __str__(self):
        return "[%s]: %50s" % (self.puzzle, self.content)


class ChatMessage(models.Model):
    id = models.AutoField(max_length=11, null=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=CASCADE)
    chatroom = models.ForeignKey('ChatRoom', on_delete=CASCADE)
    content = models.TextField(_('content'), null=False)
    created = models.DateTimeField(
        _("created"), null=True, default=timezone.now)
    editTimes = models.IntegerField(_("edit times"), null=False, default=0)

    class Meta:
        verbose_name = _("ChatMessage")

    def __str__(self):
        return "[%s]: {%s} puts {%50s}" % (self.chatroom, self.user,
                                           self.content)


class ChatRoom(models.Model):
    id = models.AutoField(max_length=11, null=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=CASCADE)
    name = models.CharField(
        _('channel'), max_length=255, null=False, unique=True)
    description = models.TextField(_('description'), null=True)
    created = models.DateField(_("created"), null=False, default=timezone.now)

    class Meta:
        verbose_name = _("ChatRoom")

    def __str__(self):
        return self.name


class FavoriteChatRoom(models.Model):
    id = models.AutoField(max_length=11, null=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=CASCADE)
    chatroom = models.ForeignKey(ChatRoom, on_delete=CASCADE)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=CASCADE)
    content = models.TextField(_('content'), null=False)
    spoiler = models.BooleanField(_('spoiler'), default=False)

    class Meta:
        verbose_name = _("Comment")

    def __str__(self):
        return "{%s} commented on {%s}" % (self.user, self.puzzle.title)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=CASCADE)
    value = models.FloatField(_('Value'), null=False, default=0)

    class Meta:
        verbose_name = _("Bookmark")

    def __str__(self):
        return "%s -- %.1f --> %s" % (self.user, self.value, self.puzzle)


class Star(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=CASCADE)
    value = models.FloatField(_('Value'), null=False, default=0)

    class Meta:
        verbose_name = _("Star")

    def __str__(self):
        return "%s -- %.1f --> %s" % (self.user, self.value, self.puzzle)
