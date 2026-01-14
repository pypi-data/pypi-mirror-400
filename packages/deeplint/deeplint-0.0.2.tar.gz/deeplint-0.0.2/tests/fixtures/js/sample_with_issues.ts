// TypeScript file with AI slop patterns
interface User {
  id: number;
  name: string;
}

function getUserData(): User {
  // obviously this works
  const user: User = {
    id: 1,
    name: "Test"
  };
  console.log("DEBUG: user =", user);

  // TODO: fetch from API
  
  return user;
}

// should work hopefully
function processUsers(users: User[]): number {
  return users.length;
}

// var instead of const/let
var globalConfig = "bad practice";
