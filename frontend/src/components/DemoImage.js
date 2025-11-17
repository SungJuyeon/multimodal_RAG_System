import React, { useEffect, useState } from "react";

function DemoImage({ convId }) {
  const [imageBase64, setImageBase64] = useState(null);

  useEffect(() => {
    async function fetchImage() {
      try {
        const res = await fetch(`http://localhost:8000/demo/image/${convId}`);
        const data = await res.json();
        setImageBase64(data.image_base64);
      } catch (err) {
        console.error("이미지 가져오기 실패", err);
      }
    }

    fetchImage();
  }, [convId]);

  if (!imageBase64) return <div>{imageBase64 === null ? "이미지 로딩 중..." : "이미지 없음"}</div>;

  return (
    <div className="demo-image">
      <img
        src={`data:image/jpeg;base64,${imageBase64.replace(/\n/g, '')}`}
        alt="Demo from vector DB"
        className="max-w-xs rounded-lg"
      />
    </div>
  );
}

export default DemoImage;