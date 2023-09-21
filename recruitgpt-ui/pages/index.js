import Image from 'next/image'
import { Inter } from 'next/font/google'
import React, { use } from 'react';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { isLoggedin,logout, getUsername, removeUsernameAfterTimeout } from "/utility/auth.js";
import styles from '../styles/Home.module.css';
import axios from 'axios';

const inter = Inter({ subsets: ['latin'] })

export default function Home() {

  const [isLogged, setIsLogged] = useState(false);
  const [username, setUsername] = useState("");
  const [files, setFiles] = useState([]);
  const [description, setDescription] = useState('');
  const [data, setData] = useState([]);
  const [showDiv, setShowDiv] = useState(false);
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { q } = router.query;

  if (q) {

    localStorage.setItem('token', q);
    localStorage.setItem('username', q);
    window.location.href = '/'

  }

  useEffect(() => {
    isLoggedin().then((res) => {
      setIsLogged(res);
    });
    setUsername(getUsername());
    removeUsernameAfterTimeout();

  }, []);

  const handleFileChange = (e) => {
    const selectedFiles = e.target.files;
    setFiles(selectedFiles);
  };

  const handleDescriptionChange = (e) => {
    setDescription(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogged) {
      const url = `/`
      router.push(url);
      if (files.length === 0) {
        alert('Please select one or more files');
        return;
      }
  
      setLoading(true);
  
      const formData = new FormData();
      for (const file of files) {
        formData.append('file', file);
      }
      // Add the description to the FormData
      formData.append('description', description);
  
      try {
        const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
  
        // Handle the response as needed
        setData(response.data.data);
        console.log(response.data);
        setShowDiv(true);
        setLoading(false);
      } catch (error) {
        console.error('Error uploading files:', error);
      }
    }
    else {
      router.push('/login');
      return;
    }

    // if (files.length === 0) {
    //   alert('Please select one or more files');
    //   return;
    // }

    // setLoading(true);

    // const formData = new FormData();
    // for (const file of files) {
    //   formData.append('file', file);
    // }
    // // Add the description to the FormData
    // formData.append('description', description);

    // try {
    //   const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
    //     headers: {
    //       'Content-Type': 'multipart/form-data',
    //     },
    //   });

    //   // Handle the response as needed
    //   setData(response.data.data);
    //   console.log(response.data);
    //   setShowDiv(true);
    //   setLoading(false);
    // } catch (error) {
    //   console.error('Error uploading files:', error);
    // }
  };

  const handleDownloadClick = () => {
    // Function to trigger the CSV download
    const csvData = data.map((item) => {
      return `${item.File_Name},${item.Score},${item['Score Explanation']}`;
    });
    const csvContent = `File_Name,Score,Score Explanation\n${csvData.join('\n')}`;

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'result.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // function handlelogin() {

  //   if (isLogged) {
  //     const url = `/`
  //     router.push(url);
  //   }

  //   else {
  //     router.push('/login');
  //   }

  // };
  return (
    <div className='no-scrollbar'>
      <main className={styles.main}>
        <div>
          <div className="absolute top-0 right-0 mt-4 mr-4">
            <div>
              {isLogged?
              <button className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded" onClick={() => {
                logout();
                router.push('/');
                window.location.reload();
              }}>
              Logout
            </button>
            :
            <>
              <button className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded" onClick={() => {
                router.push('/login');
              }}>
                Login
              </button>
              <button className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded ml-2" onClick={() => {
                router.push('/login');
              }}>
                Signup
              </button>
            </>
              }
            </div>
            
          </div>
          <div >
            <div className="text-center mx-auto my-2 px-1 py-4">
              <div className='text-bold text-xl text-white '>
                <h1 className={styles.heading}>Recruit Buddy</h1>
              </div>  
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <form onSubmit={handleSubmit}>
              <div>
                <textarea type="text" id="message" rows={5} cols={60} placeholder="Description" value={description} onChange={handleDescriptionChange} style={{ color: 'black', backgroundColor: 'white' }} ></textarea>
              </div>
              <div>
                <label htmlFor="resume">Upload Resume:</label>
                <input type="file" id="resume" accept=".docx,.pdf,.txt" multiple onChange={handleFileChange} />
              </div>
              <div>
                <button type="submit" className='rounded-md border border-gray-600 px-4 py-2 mx-auto my-2 text-center text-sm font-sm text-white w-25 hover:bg-[#2B2C2F]'>Submit</button>
              </div>
            </form>
          </div>
          <div>
          {loading ?
          (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Fetching your results...</p>
            </div>
          )
          : 
          (showDiv &&(
            <div>
              <h1 className={styles.results}>Resume results</h1>
              <table>
                <thead>
                  <tr>
                    <th>File Name</th>
                    <th>Score</th>
                    <th>Score Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, index) => (
                    <tr key={index}>
                      <td>{item.File_Name}</td>
                      <td>{item.Score}</td>
                      <td>{item['Score Explanation']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button onClick={handleDownloadClick} className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded" >Download CSV</button>
            </div>
          ))}
          </div>
          <div className={styles.footer}>
            <p>
              Powered by <a href="https://onfocussoft.com/" target="_blank">onfocus</a>, Beta Preview. RecruitGPT&trade; may produce inaccurate information occasionally. Built with ❤️ in India
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
