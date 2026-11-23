-- Allow public users to read jobs
GRANT SELECT ON public.jobs TO anon;

-- Allow authenticated users to read jobs
GRANT SELECT ON public.jobs TO authenticated;