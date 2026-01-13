import datetime

from django.conf import settings
from django.db import models


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    type = models.IntegerField()
    visibility = models.IntegerField()
    avatar = models.CharField(max_length=2048)

    assigned = models.ManyToManyField("Issue", through="IssueAssignees")

    def __str__(self):
        return self.name

    @property
    def avatar_url(self):
        return f"https://{settings.FORGEJO_HOST}/avatars/{self.avatar}"

    @property
    def html_url(self):
        return f"https://{settings.FORGEJO_HOST}/{self.name}"

    class Meta:
        managed = False
        db_table = "user"


class Repository(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField()
    updated_unix = models.BigIntegerField()
    topics = models.TextField()

    num_issues = models.IntegerField()
    num_closed_issues = models.IntegerField()
    num_pulls = models.IntegerField()
    num_closed_pulls = models.IntegerField()

    @property
    def open_issues_count(self):
        return self.num_issues - self.num_closed_issues

    @property
    def open_pr_counter(self):
        return self.num_pulls - self.num_closed_pulls

    @property
    def updated_at(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.updated_unix)

    def __str__(self):
        return self.name

    @property
    def html_url(self):
        return f"https://{settings.FORGEJO_HOST}/{self.owner.name}/{self.name}"

    @property
    def language(self):
        return self.language_set.get(is_primary=True)

    class Meta:
        managed = False
        db_table = "repository"


class Language(models.Model):
    id = models.BigAutoField(primary_key=True)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    is_primary = models.BooleanField()
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.language

    class Meta:
        managed = False
        db_table = "language_stat"


class Issue(models.Model):
    id = models.BigAutoField(primary_key=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column="repo_id")
    index = models.BigIntegerField()
    title = models.CharField(max_length=255, db_column="name")
    content = models.TextField(blank=True, null=True)
    is_closed = models.BooleanField()
    created_unix = models.BigIntegerField()
    deadline_unix = models.BigIntegerField()

    assignees = models.ManyToManyField("User", through="IssueAssignees")
    labels = models.ManyToManyField("Label", through="IssueLabel")

    @property
    def created_at(self):
        return datetime.datetime.fromtimestamp(self.created_unix)

    @property
    def due_date(self):
        return datetime.datetime.fromtimestamp(self.deadline_unix)

    @property
    def html_url(self):
        return f"https://{settings.FORGEJO_HOST}/{self.repository.owner.name}/{self.repository.name}/issues/{self.index}"

    class Meta:
        managed = False
        db_table = "issue"


class IssueAssignees(models.Model):
    id = models.BigAutoField(primary_key=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "issue_assignees"


class Label(models.Model):
    id = models.BigAutoField(primary_key=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column="repo_id")
    organization = models.ForeignKey(User, on_delete=models.CASCADE, db_column="org_id")
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = "label"


class IssueLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "issue_label"
