

const ISSERVER = typeof window === "undefined";

export const RequestHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': `Bearer ${!ISSERVER ? localStorage.getItem('token') : null}`
}


export const isLoggedin = () => new Promise((resolve, reject) => {
    if(!ISSERVER){
        const token = localStorage.getItem('token');
        if(token){
            
            resolve(true)
        }
        else {
            resolve(false)
        }

    }
})

export const getUsername = () => {
    if(!ISSERVER){
        const username = localStorage.getItem('username');
        return username
    }
}


export const logout = () => {
    if(!ISSERVER){
        localStorage.removeItem('token');
        localStorage.removeItem('username');
    }
}

const logoutDuration = 86400000; // 1 day in milliseconds

export const  removeUsernameAfterTimeout = () => {

  setTimeout(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');

  }, logoutDuration);
}



export const login = (token, username) => {
    if(!ISSERVER){
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
    }
    removeUsernameAfterTimeout();

}

export const getToken = () => {
    if(!ISSERVER){
        return localStorage.getItem('token');
    }
}

