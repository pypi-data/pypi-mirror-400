from typing import TYPE_CHECKING, List, Optional, Union

from LOGS.Auxiliary.Decorators import Endpoint
from LOGS.Entities.ProjectPersonPermission import ProjectPersonPermission
from LOGS.Entity.EntityWithIntId import IEntityWithIntId
from LOGS.Interfaces.IEntryRecord import IEntryRecord
from LOGS.Interfaces.ILockableEntity import ILockableEntity
from LOGS.Interfaces.IModificationRecord import IModificationRecord
from LOGS.Interfaces.INamedEntity import INamedEntity
from LOGS.Interfaces.IOwnedEntity import IOwnedEntity
from LOGS.Interfaces.IPermissionedEntity import IGenericPermissionEntity
from LOGS.Interfaces.ITypedEntity import ITypedEntity
from LOGS.Interfaces.IUniqueEntity import IUniqueEntity
from LOGS.LOGSConnection import LOGSConnection

if TYPE_CHECKING:
    from LOGS.Entities.Person import Person
    from LOGS.Entities.PersonMinimal import PersonMinimal


@Endpoint("projects")
class Project(
    IEntityWithIntId,
    IUniqueEntity,
    INamedEntity,
    ITypedEntity,
    IOwnedEntity,
    IEntryRecord,
    IModificationRecord,
    ILockableEntity,
    IGenericPermissionEntity,
):

    _projectPersonPermissions: Optional[List[ProjectPersonPermission]] = None

    def __init__(
        self,
        ref=None,
        id: Optional[int] = None,
        connection: Optional[LOGSConnection] = None,
        name: Optional[str] = None,
    ):
        """Represents a connected LOGS entity type"""

        self._name = name
        super().__init__(ref=ref, id=id, connection=connection)

    def personPermission(self, personIdOrPerson: Union[int, "PersonMinimal", "Person"]):
        if isinstance(personIdOrPerson, int):
            personIdOrPerson = PersonMinimal(id=personIdOrPerson)

        if self._projectPersonPermissions and personIdOrPerson:
            for p in self._projectPersonPermissions:
                if p.person and p.person.id == personIdOrPerson.id:
                    return p
        return None

    def removePersonPermission(
        self, personIdOrPerson: Union[int, "PersonMinimal", "Person"]
    ):
        if self._projectPersonPermissions is None:
            return []

        if isinstance(personIdOrPerson, int):
            personIdOrPerson = PersonMinimal(id=personIdOrPerson)

        removed = []
        projectPersonPermissions = []
        for p in self._projectPersonPermissions:
            if p.person and p.person.id == personIdOrPerson.id:
                removed.append(p)
            else:
                projectPersonPermissions.append(p)
        self._projectPersonPermissions = projectPersonPermissions

        return removed

    def addPersonPermission(
        self,
        person: Optional[Union["PersonMinimal", "Person"]] = None,
        administer: Optional[bool] = None,
        edit: Optional[bool] = None,
        add: Optional[bool] = None,
        addCurrentUserAsAdministrator: bool = False,
    ):
        from LOGS.Entities.PersonMinimal import PersonMinimal

        if not self._projectPersonPermissions:
            self._projectPersonPermissions = []

        personPermissions: List[ProjectPersonPermission] = []

        if addCurrentUserAsAdministrator:

            p = self._fetchCurrentUserMinimal()
            permission = self.personPermission(p)
            addPermission = False
            if not permission:
                addPermission = True
                permission = ProjectPersonPermission(connection=self._getConnection())
                permission.person = p
            permission.administer = True
            if addPermission:
                self._projectPersonPermissions.append(permission)
            personPermissions.append(permission)

        if person:
            p = self.checkAndConvert(
                person,
                PersonMinimal,
                self.addPersonPermission.__name__ + "(person)",
            )
            p.printContent()
            permission = self.personPermission(p)

            addPermission = False
            if not permission:
                addPermission = True
                permission = ProjectPersonPermission(connection=self._getConnection())
                permission.person = p
            permission.administer = administer
            permission.edit = edit
            permission.add = add
            if addPermission:
                self._projectPersonPermissions.append(permission)
            personPermissions.append(permission)

        if not personPermissions:
            raise ValueError("No person permissions were added.")

        return personPermissions

    @property
    def projectPersonPermissions(self) -> Optional[List[ProjectPersonPermission]]:
        return self._projectPersonPermissions

    @projectPersonPermissions.setter
    def projectPersonPermissions(self, value):
        self._projectPersonPermissions = self.checkListAndConvertNullable(
            value, ProjectPersonPermission, "projectPersonPermissions"
        )
