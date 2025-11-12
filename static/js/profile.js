// Profile Page JavaScript
// Complete implementation with notes functionality

// Store original values
let originalUsername = '';
let profilePhotoURL = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Store original username
    const usernameField = document.getElementById('username');
    if (usernameField) {
        originalUsername = usernameField.value;
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Add fade-in animation for flash messages
    flashMessages.forEach(message => {
        message.style.opacity = '1';
        message.style.transition = 'opacity 0.3s ease';
    });

    // Load saved notes
    const savedNotes = localStorage.getItem('quickNotes');
    const lastSaved = localStorage.getItem('notesSavedTime');
    if (savedNotes) {
        document.getElementById('notesArea').value = savedNotes;
    }
    if (lastSaved) {
        document.getElementById('lastSaved').textContent = lastSaved;
    }
});

// Handle photo upload (increased to 15MB)
const photoInput = document.getElementById('photoInput');
if (photoInput) {
    photoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file size (max 15MB)
            const maxSize = 15 * 1024 * 1024; // 15MB in bytes
            if (file.size > maxSize) {
                alert('File size must be less than 15MB. Your file is ' + 
                      (file.size / (1024 * 1024)).toFixed(2) + 'MB');
                photoInput.value = '';
                return;
            }

            // Validate file type
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                alert('Please select a valid image file (PNG, JPG, JPEG, or GIF)');
                photoInput.value = '';
                return;
            }

            // Read and display the image
            const reader = new FileReader();
            reader.onload = function(event) {
                profilePhotoURL = event.target.result;
                
                // Update the profile photo display
                const profilePhoto = document.getElementById('profilePhoto');
                if (profilePhoto) {
                    profilePhoto.innerHTML = 
                        `<img src="${event.target.result}" alt="Profile Photo">`;
                }
                
                // Store in hidden input for form submission
                const photoDataInput = document.getElementById('profilePhotoData');
                if (photoDataInput) {
                    photoDataInput.value = event.target.result;
                }
            };
            
            reader.onerror = function() {
                alert('Error reading file. Please try again.');
                photoInput.value = '';
            };
            
            reader.readAsDataURL(file);
        }
    });
}

// Toggle password visibility
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    const button = field.parentElement.querySelector('.toggle-password');
    if (!button) return;
    
    if (field.type === 'password') {
        field.type = 'text';
        button.textContent = 'Hide';
    } else {
        field.type = 'password';
        button.textContent = 'Show';
    }
}

// Check password strength
function checkPasswordStrength(password) {
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    let strength = 0;
    if (hasUpperCase) strength++;
    if (hasLowerCase) strength++;
    if (hasNumbers) strength++;
    if (hasSpecialChar) strength++;
    if (password.length >= 8) strength++;
    
    return {
        score: strength,
        hasUpperCase,
        hasLowerCase,
        hasNumbers,
        hasSpecialChar
    };
}

// Handle form submission with validation
const profileForm = document.getElementById('profileForm');
if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
        const username = document.getElementById('username');
        const currentPassword = document.getElementById('currentPassword');
        const newPassword = document.getElementById('newPassword');
        const confirmPassword = document.getElementById('confirmPassword');

        if (!username || !currentPassword || !newPassword || !confirmPassword) {
            return; // Let the form submit normally if elements not found
        }

        const usernameValue = username.value.trim();
        const currentPasswordValue = currentPassword.value;
        const newPasswordValue = newPassword.value;
        const confirmPasswordValue = confirmPassword.value;

        // Validate username
        if (!usernameValue) {
            e.preventDefault();
            alert('Username cannot be empty');
            username.focus();
            return false;
        }

        if (usernameValue.length < 3) {
            e.preventDefault();
            alert('Username must be at least 3 characters long');
            username.focus();
            return false;
        }

        // Check if username contains only valid characters
        const usernameRegex = /^[a-zA-Z0-9_-]+$/;
        if (!usernameRegex.test(usernameValue)) {
            e.preventDefault();
            alert('Username can only contain letters, numbers, hyphens, and underscores');
            username.focus();
            return false;
        }

        // Validate password change if attempting to change password
        if (newPasswordValue || confirmPasswordValue) {
            if (!currentPasswordValue) {
                e.preventDefault();
                alert('Please enter your current password to change it');
                currentPassword.focus();
                return false;
            }
            
            if (newPasswordValue !== confirmPasswordValue) {
                e.preventDefault();
                alert('New passwords do not match');
                confirmPassword.focus();
                return false;
            }

            if (newPasswordValue.length < 6) {
                e.preventDefault();
                alert('New password must be at least 6 characters long');
                newPassword.focus();
                return false;
            }

            // Check password strength
            const strength = checkPasswordStrength(newPasswordValue);
            
            if (strength.score < 3) {
                const weakConfirm = confirm(
                    'Your password is weak. A strong password should contain:\n\n' +
                    (strength.hasUpperCase ? '✓' : '✗') + ' Uppercase letters\n' +
                    (strength.hasLowerCase ? '✓' : '✗') + ' Lowercase letters\n' +
                    (strength.hasNumbers ? '✓' : '✗') + ' Numbers\n' +
                    (strength.hasSpecialChar ? '✓' : '✗') + ' Special characters\n' +
                    (newPasswordValue.length >= 8 ? '✓' : '✗') + ' At least 8 characters\n\n' +
                    'Do you want to continue with this password?'
                );
                
                if (!weakConfirm) {
                    e.preventDefault();
                    newPassword.focus();
                    return false;
                }
            }
        }

        // Show loading state
        const submitButton = profileForm.querySelector('.save-btn');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Saving...';
        }

        // Form will submit normally
        return true;
    });
}

// Reset form function
function resetForm() {
    const username = document.getElementById('username');
    const currentPassword = document.getElementById('currentPassword');
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    const photoInput = document.getElementById('photoInput');
    const profilePhoto = document.getElementById('profilePhoto');
    const photoDataInput = document.getElementById('profilePhotoData');

    // Confirm if there are unsaved changes
    let hasChanges = false;
    
    if (username && username.value !== originalUsername) {
        hasChanges = true;
    }
    
    if (currentPassword && currentPassword.value) {
        hasChanges = true;
    }
    
    if (newPassword && newPassword.value) {
        hasChanges = true;
    }
    
    if (confirmPassword && confirmPassword.value) {
        hasChanges = true;
    }
    
    if (profilePhotoURL) {
        hasChanges = true;
    }

    if (hasChanges) {
        const confirmReset = confirm('Are you sure you want to discard all changes?');
        if (!confirmReset) {
            return;
        }
    }

    // Reset text fields
    if (username) username.value = originalUsername;
    if (currentPassword) currentPassword.value = '';
    if (newPassword) newPassword.value = '';
    if (confirmPassword) confirmPassword.value = '';
    
    // Reset profile photo
    if (profilePhotoURL && profilePhoto) {
        profilePhotoURL = null;
        if (photoDataInput) photoDataInput.value = '';
        
        // Restore default SVG icon
        profilePhoto.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" height="70px" viewBox="0 -960 960 960" width="70px" fill="#588157">
                <path d="M226-262q59-39.67 121-60.83Q409-344 480-344t133.33 21.17q62.34 21.16 121.34 60.83 41-49.67 59.83-103.67T813.33-480q0-141-96.16-237.17Q621-813.33 480-813.33t-237.17 96.16Q146.67-621 146.67-480q0 60.33 19.16 114.33Q185-311.67 226-262Zm253.88-184.67q-58.21 0-98.05-39.95Q342-526.58 342-584.79t39.96-98.04q39.95-39.84 98.16-39.84 58.21 0 98.05 39.96Q618-642.75 618-584.54t-39.96 98.04q-39.95 39.83-98.16 39.83ZM479.73-80q-83.1 0-156.18-31.5-73.09-31.5-127.15-85.83-54.07-54.34-85.23-127.23Q80-397.45 80-480.33q0-82.88 31.5-155.78Q143-709 197.33-763q54.34-54 127.23-85.5T480.33-880q82.88 0 155.78 31.5Q709-817 763-763t85.5 127Q880-563 880-480.18q0 82.83-31.5 155.67Q817-251.67 763-197.33 709-143 635.91-111.5 562.83-80 479.73-80Z"/>
            </svg>
        `;
    }
    
    // Clear file input
    if (photoInput) photoInput.value = '';

    // Reset all password toggles to "Show"
    document.querySelectorAll('.toggle-password').forEach(btn => {
        const field = btn.parentElement.querySelector('input');
        if (field) {
            field.type = 'password';
            btn.textContent = 'Show';
        }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Notes functions
function saveNotes(event) {
    const notes = document.getElementById('notesArea').value;
    localStorage.setItem('quickNotes', notes);
    
    const now = new Date();
    const timeString = now.toLocaleString();
    localStorage.setItem('notesSavedTime', timeString);
    document.getElementById('lastSaved').textContent = timeString;
    
    // Show success feedback
    const button = event ? event.target : document.querySelector('.save-notes-btn');
    if (button) {
        const originalText = button.textContent;
        const originalBg = button.style.backgroundColor;
        button.textContent = 'Saved!';
        button.style.backgroundColor = '#588157';
        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = originalBg;
        }, 1500);
    }
}

function clearNotes() {
    if (confirm('Are you sure you want to clear all notes?')) {
        document.getElementById('notesArea').value = '';
        localStorage.removeItem('quickNotes');
        localStorage.removeItem('notesSavedTime');
        document.getElementById('lastSaved').textContent = 'Never';
    }
}

// Auto-save notes every 30 seconds
setInterval(() => {
    const notes = document.getElementById('notesArea').value;
    if (notes.trim()) {
        localStorage.setItem('quickNotes', notes);
    }
}, 30000);

// Add visual feedback for form fields
const formInputs = document.querySelectorAll('input[type="text"], input[type="password"]');
formInputs.forEach(input => {
    // Add focus effect
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.classList.remove('focused');
    });
    
    // Add change indicator
    input.addEventListener('input', function() {
        if (this.value !== this.defaultValue) {
            this.style.borderColor = '#588157';
        } else {
            this.style.borderColor = '#a3b18a';
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const submitButton = document.querySelector('.save-btn');
        if (submitButton) {
            submitButton.click();
        }
    }
    
    // Escape to cancel
    if (e.key === 'Escape') {
        const cancelButton = document.querySelector('.cancel-btn');
        if (cancelButton) {
            cancelButton.click();
        }
    }
});

// Warn user before leaving page with unsaved changes
window.addEventListener('beforeunload', function(e) {
    const username = document.getElementById('username');
    const currentPassword = document.getElementById('currentPassword');
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    
    let hasChanges = false;
    
    if (username && username.value !== originalUsername) hasChanges = true;
    if (currentPassword && currentPassword.value) hasChanges = true;
    if (newPassword && newPassword.value) hasChanges = true;
    if (confirmPassword && confirmPassword.value) hasChanges = true;
    if (profilePhotoURL) hasChanges = true;
    
    if (hasChanges) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Console log for debugging (remove in production)
console.log('Profile page JavaScript loaded successfully');
console.log('Original username:', originalUsername);