import React from 'react';
import type { UploadProps } from 'antd';
import { ConfigProvider, message, Upload } from 'antd';

interface DropFileInputProps {
  callback: () => void;
}

const DropFileInput:  React.FC<DropFileInputProps> = ({callback}) => {
  
  const { Dragger } = Upload;

  const props: UploadProps = {
    name: 'file',
    multiple: false,
    accept: ".csv",
    action: `http://localhost:${import.meta.env.VITE_APP_API_PORT}/uploadfile/`,
    showUploadList: false,
    onChange(info) {
      const { status } = info.file;
      if (status === 'done') {
        callback();
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
  };
  
  return(
    <ConfigProvider
      theme={{
        components: {
          Upload: {
            colorPrimaryHover: "#50c777"
          },
        },
      }}
    >
    <Dragger {...props}>
      <p className='text-[#bdbdbd]'>Click or drag file to this area to upload</p>
    </Dragger>
    </ConfigProvider>
  );
}

export default DropFileInput;