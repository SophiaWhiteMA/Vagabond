const username = /^[a-zA-Z0-9_-]{1,32}$/g;

const actor = /^[a-zA-Z0-9_-]{1,32}$/g;

const password = /^.{12,255}/g;

const actorHandle = /@[\w]{1,}@([\w]{1,}\.){0,}[\w]{1,}\.[\w]{1,}/g;

export {actorHandle, username, actor, password}

