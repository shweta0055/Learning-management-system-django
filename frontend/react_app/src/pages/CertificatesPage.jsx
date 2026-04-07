import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { certificatesAPI } from '../services/api';
import { toast } from 'react-toastify';

export default function CertificatesPage() {
  const { data: certs, isLoading, refetch } = useQuery({
    queryKey: ['my-certificates'],
    queryFn: () => certificatesAPI.myCertificates(),
    select: (r) => r.data.results || r.data,
  });

  const downloadMutation = useMutation({
    mutationFn: (certId) => certificatesAPI.verify(certId),
    onSuccess: () => toast.info('Downloading certificate...'),
  });

  if (isLoading) return <div className="text-center py-20">Loading certificates...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">My Certificates</h1>
      {certs?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {certs.map((cert) => (
            <div key={cert.id} className="card p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">
                  🏅
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{cert.course_title}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Issued {new Date(cert.issued_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                  </p>
                  <p className="text-xs text-gray-400 mt-1 font-mono">{cert.certificate_id}</p>
                </div>
              </div>
              <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
                {cert.pdf_file && (
                  <a href={cert.pdf_file} download className="btn-primary text-xs py-1.5 px-3">
                    ⬇ Download
                  </a>
                )}
                <a
                  href={`/api/certificates/verify/${cert.certificate_id}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-secondary text-xs py-1.5 px-3"
                >
                  🔗 Share
                </a>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-gray-400">
          <div className="text-5xl mb-4">🏅</div>
          <p className="text-lg">No certificates yet</p>
          <p className="text-sm mt-2">Complete courses to earn your certificates</p>
        </div>
      )}
    </div>
  );
}
