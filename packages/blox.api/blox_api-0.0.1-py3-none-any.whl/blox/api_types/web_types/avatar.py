"""

avatar.roblox.com

"""

from typing import Optional, TypedDict, List


class v1_UserAvatarScales(TypedDict):
    height: int
    width: int
    head: int
    depth: int
    proportion: int
    bodyType: int


class v1_UserAvatarBodyColors(TypedDict):
    headColorId: int
    torsoColorId: int
    rightArmColorId: int
    leftArmColorId: int
    rightLegColorId: int
    leftLegColorId: int


class v1_UserAvatar3DVector(TypedDict):
    X: int
    Y: int
    Z: int


class v1_UserAvatarAssetType(TypedDict):
    id: int
    name: str


class v1_UserAvatarAssetMeta(TypedDict):
    order: int
    puffiness: int
    position: v1_UserAvatar3DVector
    rotation: v1_UserAvatar3DVector
    scale: v1_UserAvatar3DVector
    headShape: int
    version: int


class v1_UserAvatarAsset(TypedDict):
    id: int
    name: str
    assetType: v1_UserAvatarAssetType
    currentVersionId: int
    meta: Optional[v1_UserAvatarAssetMeta]
    availabilityStatus: Optional[str]
    expirationTime: Optional[str]
    isSwappable: Optional[bool]


class v1_UserAvatarEmote(TypedDict):
    assetId: int
    assetName: str
    position: int


class v2_UserAvatarBodyColors(TypedDict):
    headColor3: str
    torsoColor3: str
    rightArmColor3: str
    leftArmColor3: str
    rightLegColor3: str
    leftLegColor3: str


# GET https://avatar.roblox.com/v1/users/{userId}/currently-wearing
class v1_UseryWearingAssetIdsResponse(TypedDict):
    assetIds: List[int]


# GET https://avatar.roblox.com/v1/users/{userId}/avatar
class v1_UserAvatarDetails(TypedDict):
    scales: v1_UserAvatarScales
    playerAvatarType: str
    bodyColors: v1_UserAvatarBodyColors
    assets: List[v1_UserAvatarAsset]
    defaultShirtApplied: bool
    defaultPantsApplied: bool
    emotes: List[v1_UserAvatarEmote]


# GET https://avatar.roblox.com/v2/avatar/users/{userId}/avatar
class v2_UserAvatarDetails(TypedDict):
    scales: v1_UserAvatarScales
    playerAvatarType: str
    bodyColors: v2_UserAvatarBodyColors
    assets: List[v1_UserAvatarAsset]
    defaultShirtApplied: bool
    defaultPantsApplied: bool
    emotes: List[v1_UserAvatarEmote]
