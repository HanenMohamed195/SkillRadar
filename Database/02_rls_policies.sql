-- Public read access for jobs
CREATE POLICY "Public can read jobs"
ON public.jobs
FOR SELECT
TO anon, authenticated
USING (true);


-- Public read access for skills
CREATE POLICY "Public can read skills"
ON public.skills
FOR SELECT
TO anon, authenticated
USING (true);


-- Public read access for job skills
CREATE POLICY "Public can read job skills"
ON public.job_skills
FOR SELECT
TO anon, authenticated
USING (true);


-- Users can view their own profile
CREATE POLICY "Users can view own profile"
ON public.profiles
FOR SELECT
TO authenticated
USING (auth.uid() = id);


-- Users can insert their own profile
CREATE POLICY "Users can insert own profile"
ON public.profiles
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);


-- Users can update their own profile
CREATE POLICY "Users can update own profile"
ON public.profiles
FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);


-- Users can manage their own skills
CREATE POLICY "Users manage own skills"
ON public.user_skills
FOR ALL
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);


-- Users can manage their own saved jobs
CREATE POLICY "Users manage own saved jobs"
ON public.saved_jobs
FOR ALL
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);