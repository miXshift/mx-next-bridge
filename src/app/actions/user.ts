// src/app/actions/user.ts
'use server'

import { revalidatePath } from 'next/cache';
import connectDB from '@mx-service/lib/db';
import User from '@mx-service/models/User';
import { getServerAuthSession } from '@mx-service/lib/auth';

export async function createUser(formData: FormData) {
  const session = await getServerAuthSession();
  
  // Check if user is admin
  if (!session?.user?.isAdmin) {
    return { error: 'Not authorized' };
  }

  try {
    await connectDB();
    
    const name = formData.get('name') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    
    // Validate input
    if (!name || !email || !password) {
      return { error: 'All fields are required' };
    }

    // Check if user already exists
    const userExists = await User.findOne({ email });
    if (userExists) {
      return { error: 'User already exists' };
    }

    // Create user
    const user = await User.create({
      name,
      email,
      password,
    });

    revalidatePath('/admin/users');
    return { success: true, user: { id: user._id, name: user.name, email: user.email } };
  } catch (error) {
    console.error('Error creating user:', error);
    return { error: 'Failed to create user' };
  }
}

export async function getUsers() {
  const session = await getServerAuthSession();
  
  // Check if user is admin
  if (!session?.user?.isAdmin) {
    return { error: 'Not authorized' };
  }

  try {
    await connectDB();
    const users = await User.find().select('-password');
    return { success: true, users };
  } catch (error) {
    console.error('Error fetching users:', error);
    return { error: 'Failed to fetch users' };
  }
}