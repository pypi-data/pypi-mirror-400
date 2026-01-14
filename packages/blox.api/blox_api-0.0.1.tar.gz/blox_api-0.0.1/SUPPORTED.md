Below as an up-to-date list of all Roblox API endpoints supported by `blox.api`.  
Do not hesitate to request (or contribute) support for additional endpoints below.

> https://github.com/TychoTeam/blox.api-py/issues

## Web APIs

#### `avatar.roblox.com`

```http
GET https://avatar.roblox.com/v1/users/{userId}/currently-wearing
GET https://avatar.roblox.com/v1/users/{userId}/avatar
GET https://avatar.roblox.com/v2/avatar/users/{userId}/avatar
```

#### `groups.roblox.com`

```http
GET https://groups.roblox.com/v1/users/{userId}/groups/roles
GET https://groups.roblox.com/v1/groups/{groupId}
GET https://groups.roblox.com/v1/groups/{groupId}/users
GET https://groups.roblox.com/v1/groups/{groupId}/roles
GET https://groups.roblox.com/v1/groups/{groupId}/name-history
GET https://groups.roblox.com/v1/groups/{groupId}/roles/{roleSetId}/users
```

#### `users.roblox.com`

```http
GET https://users.roblox.com/v1/users/{userId}
GET https://users.roblox.com/v1/users/{userId}/username-history
POST https://users.roblox.com/v1/usernames/users
POST https://users.roblox.com/v1/users
GET https://users.roblox.com/v1/users/search
GET https://users.roblox.com/v1/users/authenticated
```

The following undocumented user-related API endpoints are also supported.

```http
GET https://apis.roblox.com/search-api/omni-search
```

#### `thumbnails.roblox.com`

```http
GET https://thumbnails.roblox.com/v1/groups/icons
GET https://thumbnails.roblox.com/v1/users/avatar
GET https://thumbnails.roblox.com/v1/users/avatar-bust
GET https://thumbnails.roblox.com/v1/users/avatar-headshot
```
