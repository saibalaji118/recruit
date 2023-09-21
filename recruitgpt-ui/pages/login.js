import Head from "next/head";
import {motion} from "framer-motion";
import {useEffect, useState, useCallback} from "react";
import { isLoggedin, login } from "/utility/auth.js";
import {BACKEND_URL, client_id} from "../utility/constants.js";
import { useRouter } from 'next/router.js';
import NextScript from 'next/script';

const Login = ({type}) => {
    const [isLogged, setIsLogged] = useState(false);
    const [title, setTitle] = useState("Welcome");

    const router = useRouter();

    useEffect(() => {
        isLoggedin().then((res) => {
            setIsLogged(res);
        });
    }, []);

    const openGoogleLoginPage = useCallback(() => {
        const googleAuthUrl = 'https://accounts.google.com/o/oauth2/v2/auth';
        const redirectUri = 'api/v1/auth/login/google/';
  
        const scope = [
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile'
        ].join(' ');
  
        const params = {
          response_type: 'code',
          client_id: client_id,
          // need to change
          redirect_uri: `http://127.0.0.1:5000/login`,
          prompt: 'select_account',
          access_type: 'offline',
          scope
        }
  
        const urlParams = new URLSearchParams(params).toString();
  
        window.location = `${googleAuthUrl}?${urlParams}`;
  
      }, []);

    return(
        <div>
            <Head>
                <title>Login - RecruitGPT</title>

            </Head>
            <div className=" mx-auto flex flex-col justify-between items-center py-20 mt-20 lg:w-1/3 md:w-1/2 rounded-3xl shadow-2xl border-1 border-neutral-200 no-scrollbar">

                <motion.div
                    animate={{ scale: [0.8, 1] }}
                    transition={{ duration: 0.3 }}
                    className="flex flex-col justify-center items-center container py-20 lg:w-80"
                >
                <h1 className="font-bold text-3xl mb-2">{title}</h1>
              

                <hr></hr>

                <div className="flex items-center py-5">
                  <div className="border-t w-36 border-gray-400"></div>
                  {/*<span className="px-3 text-xs">OR</span>*/}
                  <div className="border-t w-36 border-gray-400"></div>
                </div>

                <div onClick={openGoogleLoginPage} className="mt-4 p-3 border border-gray-400 rounded-sm w-80 hover:bg-gray-200 flex">
                  <img className="w-5 h-5 mr-4" src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png" />
                  <span className="text-center">Continue with Google</span>
                </div>

                <NextScript />

                    

                </motion.div>

            </div>
        </div>
    )
}



Login.getInitialProps = ({ query }) => {
    return { type: query.type };
  };
  
  export default Login;