import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { FileText, Upload, Loader2, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { uploadResume } from '../services/api';

const UploadResumePage = () => {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const onDrop = (acceptedFiles) => {
        const selectedFile = acceptedFiles[0];
        if (selectedFile?.type === 'application/pdf') {
            setFile(selectedFile);
            setError(null);
        } else {
            setError('Please upload a PDF file.');
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        multiple: false
    });

    const handleUpload = async () => {
        if (!file) return;

        setIsLoading(true);
        setError(null);

        try {
            console.log("Starting upload for file:", file.name);
            const response = await uploadResume(file);
            console.log("Upload success:", response);
            // Navigate to interview setup or start
            navigate(`/interview/${response.resume_id}`, { state: { analysis: response.analysis } });
        } catch (err) {
            console.error("Upload error caught in component:", err);
            let detail = "Please try again.";

            if (err.response) {
                // Server responded with a status code outside 2xx range
                console.error("Server Error Data:", err.response.data);
                console.error("Server Error Status:", err.response.status);
                detail = err.response.data?.detail || JSON.stringify(err.response.data) || `Status: ${err.response.status}`;
            } else if (err.request) {
                // Request was made but no response received
                console.error("No response received:", err.request);
                detail = "No response from server. Check connection.";
            } else {
                // Something happened in setting up the request
                console.error("Request setup error:", err.message);
                detail = err.message;
            }

            setError(`CRITICAL UPLOAD ERROR: ${detail}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen pt-24 px-4 flex flex-col items-center justify-center bg-background">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-2xl w-full space-y-8 text-center"
            >
                <div className="space-y-4">
                    <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
                        Ready for your <span className="text-blue-400">Mock Interview?</span>
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Upload your resume and let our specialized agents design a custom session for you.
                    </p>
                </div>

                <div
                    {...getRootProps()}
                    className={`
                        border-2 border-dashed rounded-3xl p-12 transition-all cursor-pointer bg-card/50 backdrop-blur-sm
                        ${isDragActive ? 'border-primary bg-primary/10' : 'border-gray-700 hover:border-primary/50 hover:bg-card'}
                        ${file ? 'border-green-500/50 bg-green-500/5' : ''}
                    `}
                >
                    <input {...getInputProps()} />
                    <div className="flex flex-col items-center space-y-4">
                        <div className={`p-4 rounded-full ${file ? 'bg-green-500/20 text-green-400' : 'bg-primary/20 text-primary'}`}>
                            {file ? <FileText size={40} /> : <Upload size={40} />}
                        </div>
                        {file ? (
                            <div className="space-y-2">
                                <p className="text-xl font-semibold text-green-400">{file.name}</p>
                                <p className="text-sm text-gray-500">Click to replace file</p>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <p className="text-xl font-semibold text-gray-200">
                                    {isDragActive ? "Drop your resume here" : "Drag & drop your resume here"}
                                </p>
                                <p className="text-sm text-gray-500">or click to browse (PDF only)</p>
                            </div>
                        )}
                    </div>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-center justify-center space-x-2"
                    >
                        <AlertCircle size={20} />
                        <span>{error}</span>
                    </motion.div>
                )}

                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleUpload}
                    disabled={!file || isLoading}
                    className={`
                        w-full py-4 rounded-xl font-semibold text-lg transition-all
                        ${!file || isLoading
                            ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                            : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40'}
                    `}
                >
                    {isLoading ? (
                        <span className="flex items-center justify-center space-x-2">
                            <Loader2 className="animate-spin" />
                            <span>Analyzing Profile...</span>
                        </span>
                    ) : (
                        "START INTERVIEW (V2 UPDATED)"
                    )}
                </motion.button>
            </motion.div>
        </div>
    );
};

export default UploadResumePage;
